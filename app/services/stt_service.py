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
        # Mock fallback should only be used in local/dev workflows.
        self.allow_mock_fallback = settings.DEBUG or (not settings.PUBLIC_DEPLOYMENT)
        
        # Try Groq API first (free, fastest)
        if settings.GROQ_API_KEY:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
                self.use_groq = True
                print("[OK] [STT] Groq API ready (whisper-large-v3)")
            except Exception as e:
                print(f"[ERROR] [STT] Groq init failed: {type(e).__name__}: {str(e)}")
        else:
            print("[ERROR] [STT] GROQ_API_KEY not set — Groq Whisper disabled!")

        # Fallback to OpenAI Whisper API
        if not self.use_groq and settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                self.use_openai = True
                print("[OK] [STT] OpenAI Whisper API ready (fallback)")
            except Exception as e:
                print(f"[ERROR] [STT] OpenAI init failed: {str(e)}")

        if not self.use_groq and not self.use_openai:
            if self.allow_mock_fallback:
                print("[ERROR] [STT] NO real STT API available — using MOCK mode (development only)")
            else:
                print("[ERROR] [STT] NO real STT API available in production — uploads will fail until STT API is configured")
    
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
        
        print(f"[AUDIO] Starting transcription: {audio_file_path}")
        
        runtime_errors = []

        # Try Groq API first (fastest, free)
        if self.use_groq:
            try:
                return await self._groq_transcribe(audio_file_path, language)
            except Exception as e:
                import traceback
                print(f"[ERROR] Groq transcription failed: {type(e).__name__}: {str(e)}")
                print(traceback.format_exc())
                runtime_errors.append(f"Groq failed: {type(e).__name__}: {str(e)}")
        
        # Fallback to OpenAI Whisper API
        if self.use_openai:
            try:
                return await self._openai_transcribe(audio_file_path, language)
            except Exception as e:
                print(f"[ERROR] OpenAI transcription failed: {type(e).__name__}: {str(e)}")
                runtime_errors.append(f"OpenAI failed: {type(e).__name__}: {str(e)}")
        
        # Final fallback to mock for local/dev only. In production, fail loudly
        # so users never receive fabricated transcript text.
        if self.allow_mock_fallback:
            print("[WARNING] FALLING BACK TO MOCK TRANSCRIPTION — real audio ignored")
            return await self._mock_transcribe(audio_file_path, language)

        providers = []
        if self.use_groq:
            providers.append("Groq")
        if self.use_openai:
            providers.append("OpenAI")
        provider_text = ", ".join(providers) if providers else "none"
        error_text = " | ".join(runtime_errors) if runtime_errors else "No STT provider available"
        raise RuntimeError(
            f"STT failed in production. Providers attempted: {provider_text}. Details: {error_text}"
        )
    
    async def _groq_transcribe(self, audio_file_path: str, language: str) -> dict:
        """
        Transcribe using Groq's Whisper API.
        Groq Whisper natively accepts: mp3, mp4, mpeg, mpga, m4a, wav, webm, ogg.
        We send the file with the correct MIME type — no conversion needed for
        the common browser formats (webm/ogg/mp4).  We only convert exotic
        formats (e.g. flac, aac) that Groq does not support.
        """
        file_size = os.path.getsize(audio_file_path)
        ext = os.path.splitext(audio_file_path)[1].lower()
        print(f"[AUDIO] Transcribing with Groq API: {audio_file_path} ({file_size} bytes, ext={ext})")

        # Groq-supported MIME types (sent as-is, no conversion needed)
        GROQ_SUPPORTED = {
            ".wav":  "audio/wav",
            ".mp3":  "audio/mp3",
            ".mp4":  "audio/mp4",
            ".mpeg": "audio/mpeg",
            ".mpga": "audio/mpeg",
            ".m4a":  "audio/m4a",
            ".webm": "audio/webm",
            ".ogg":  "audio/ogg",
        }

        send_path = audio_file_path
        send_mime = GROQ_SUPPORTED.get(ext)
        wav_created = False

        if send_mime:
            # Happy path — browser-native format, send directly
            print(f"   ✅ Format {ext} natively supported by Groq — sending directly")
        else:
            # Exotic format: attempt pydub → WAV conversion
            print(f"   🔄 Format {ext} not in Groq's supported list — converting to WAV…")
            try:
                from pydub import AudioSegment
                fmt = ext.lstrip(".")
                if fmt == "mpeg":
                    fmt = "mp3"
                audio_seg = AudioSegment.from_file(audio_file_path, format=fmt)
                send_path = audio_file_path.replace(ext, ".wav")
                audio_seg.export(send_path, format="wav")
                wav_created = True
                send_mime = "audio/wav"
                print(f"   ✅ Converted to WAV: {send_path} ({os.path.getsize(send_path)} bytes)")
            except Exception as conv_err:
                import traceback
                print(f"   ⚠️ Conversion failed — attempting with original file anyway: {conv_err}")
                print(traceback.format_exc())
                send_path = audio_file_path
                send_mime = "audio/octet-stream"

        try:
            with open(send_path, "rb") as f:
                audio_bytes = f.read()

            filename = os.path.basename(send_path)
            print(f"   📤 Sending to Groq: {filename} ({len(audio_bytes)} bytes, mime={send_mime})")
            # Use 2-tuple (name, bytes) — no explicit MIME — so Groq auto-detects
            # format from magic bytes. This is exactly what worked in production.
            # Specifying MIME risks a mismatch if content-type headers lie.
            transcription = self.groq_client.audio.transcriptions.create(
                file=(filename, audio_bytes),
                model="whisper-large-v3",
                language=language,
                response_format="json"
            )

            transcribed_text = transcription.text.strip()
            if not transcribed_text:
                raise ValueError(
                    "Groq returned empty transcription — audio may be silent, "
                    "too short, or the mic did not capture speech"
                )
            print(f"✅ Groq transcription complete: {transcribed_text[:100]}...")
            return {
                "text": transcribed_text,
                "language": language,
                "method": "groq"
            }
        finally:
            # Clean up temporary WAV file created during conversion
            if wav_created and os.path.exists(send_path):
                try:
                    os.remove(send_path)
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
