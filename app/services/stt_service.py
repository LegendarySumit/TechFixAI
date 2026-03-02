"""
Speech-to-Text service.
Handles Japanese audio transcription using cloud-based Whisper APIs.
"""

import os
import random
from typing import Optional

from app.core.config import settings
from app.utils.encryption import audio_encryption


class STTService:
    """
    Speech-to-Text service for Japanese audio.
    Priority: Groq API > OpenAI Whisper API > Mock mode
    All methods are cloud-based (no local model downloads).
    """
    
    def __init__(self):
        self.groq_client = None
        self.openai_client = None
        self.use_groq = False
        self.use_openai = False
        
        # Try Groq API first (free, fastest)
        if settings.GROQ_API_KEY:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
                self.use_groq = True
                print(f"✅ [STT] Groq API ready (whisper-large-v3) key={settings.GROQ_API_KEY[:8]}...")
            except Exception as e:
                print(f"❌ [STT] Groq init failed: {type(e).__name__}: {str(e)}")
        else:
            print("❌ [STT] GROQ_API_KEY not set — Groq Whisper disabled!")

        # Fallback to OpenAI Whisper API
        if not self.use_groq and settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                self.use_openai = True
                print("✅ [STT] OpenAI Whisper API ready (fallback)")
            except Exception as e:
                print(f"❌ [STT] OpenAI init failed: {str(e)}")

        if not self.use_groq and not self.use_openai:
            print("❌ [STT] NO real STT API available — will use MOCK mode (random Japanese text!)")
    
    async def transcribe_audio(self, audio_file_path: str, language: str = "ja") -> dict:
        """
        Transcribe audio file to text using cloud APIs.
        
        Args:
            audio_file_path: Path to audio file
            language: Language code (default: ja for Japanese)
        
        Returns:
            dict with:
                - text: Transcribed text
                - language: Detected language
                - method: Transcription method used
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        print(f"🎤 Starting transcription: {audio_file_path}")
        
        # Try Groq API first (fastest, free)
        if self.use_groq:
            try:
                return await self._groq_transcribe(audio_file_path, language)
            except Exception as e:
                import traceback
                print(f"❌ Groq transcription failed: {type(e).__name__}: {str(e)}")
                print(traceback.format_exc())
        
        # Fallback to OpenAI Whisper API
        if self.use_openai:
            try:
                return await self._openai_transcribe(audio_file_path, language)
            except Exception as e:
                print(f"❌ OpenAI transcription failed: {type(e).__name__}: {str(e)}")
        
        # Final fallback to mock — log clearly so user knows
        print("⚠️⚠️⚠️ FALLING BACK TO MOCK TRANSCRIPTION — real audio ignored")
        return await self._mock_transcribe(audio_file_path, language)
    
    async def _groq_transcribe(self, audio_file_path: str, language: str) -> dict:
        """
        Transcribe using Groq's Whisper API.
        Converts any browser format (webm/ogg/mp4) to WAV first — WAV is
        universally accepted by Whisper and avoids codec rejection errors.
        """
        file_size = os.path.getsize(audio_file_path)
        ext = os.path.splitext(audio_file_path)[1].lower()
        print(f"🎤 Transcribing with Groq API: {audio_file_path} ({file_size} bytes, ext={ext})")

        # ── Convert non-WAV audio to WAV via pydub (ffmpeg backend) ──────────
        wav_path = audio_file_path  # default: use as-is
        wav_created = False
        if ext != ".wav":
            try:
                from pydub import AudioSegment
                fmt = ext.lstrip(".")          # "webm", "ogg", "mp4", "mp3" …
                if fmt == "mpeg":
                    fmt = "mp3"
                print(f"   🔄 Converting {ext} → WAV for Groq compatibility...")
                audio_seg = AudioSegment.from_file(audio_file_path, format=fmt)
                wav_path = audio_file_path.replace(ext, ".wav")
                audio_seg.export(wav_path, format="wav")
                wav_created = True
                wav_size = os.path.getsize(wav_path)
                print(f"   ✅ Converted to WAV: {wav_path} ({wav_size} bytes)")
            except Exception as conv_err:
                import traceback
                print(f"   ⚠️ Audio conversion failed, trying original file: {conv_err}")
                print(traceback.format_exc())
                wav_path = audio_file_path   # fall back to original

        try:
            with open(wav_path, "rb") as f:
                audio_bytes = f.read()

            filename = os.path.basename(wav_path)
            transcription = self.groq_client.audio.transcriptions.create(
                file=(filename, audio_bytes, "audio/wav"),
                model="whisper-large-v3",
                language=language,
                response_format="json"
            )

            transcribed_text = transcription.text.strip()
            if not transcribed_text:
                raise ValueError(
                    "Groq returned empty transcription — audio may be silent, "
                    "too short, or in the wrong language"
                )
            print(f"✅ Groq transcription complete: {transcribed_text[:100]}...")
            return {
                "text": transcribed_text,
                "language": language,
                "method": "groq"
            }
        finally:
            # Clean up temporary WAV file
            if wav_created and os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except Exception:
                    pass
    
    async def _openai_transcribe(self, audio_file_path: str, language: str) -> dict:
        """Transcribe using OpenAI Whisper API (cloud-based)."""
        print(f"🎤 Transcribing with OpenAI Whisper API: {audio_file_path}")
        
        with open(audio_file_path, "rb") as audio_file:
            transcription = self.openai_client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                language=language,
                response_format="json"
            )
        
        transcribed_text = transcription.text.strip()
        print(f"✅ OpenAI transcription complete: {transcribed_text[:100]}...")
        
        return {
            "text": transcribed_text,
            "language": language,
            "method": "openai"
        }
    
    async def _mock_transcribe(self, audio_file_path: str, language: str) -> dict:
        """
        Mock transcription for development/testing.
        Returns realistic Japanese technical support requests.
        """
        # Sample Japanese technical issues
        japanese_samples = [
            "サーバーがダウンしており、誰もアクセスできません。すぐに対応してください。",
            "データベースの接続エラーが発生しています。ログインができない状態です。",
            "APIのレスポンスが遅く、タイムアウトエラーが頻発しています。",
            "バックエンドサービスが503エラーを返しています。至急確認をお願いします。",
            "システムのパフォーマンスが低下しており、ユーザーから苦情が来ています。",
            "認証システムに問題があり、ログインできないユーザーが多数います。",
            "ファイルアップロード機能が動作していません。エラーログを確認してください。",
            "メール送信機能が停止しています。SMTP設定を確認する必要があります。",
            "キャッシュシステムがクラッシュし、全てのページが遅延しています。",
            "データベースのクエリにデッドロックが発生しています。調査をお願いします。"
        ]
        
        # Select random sample
        text = random.choice(japanese_samples)
        
        print(f"🎤 MOCK Transcription: {text}")
        
        return {
            "text": text,
            "language": language,
            "method": "mock"
        }


# Singleton instance
stt_service = STTService()
