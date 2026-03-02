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
                print("✅ Groq API configured for STT (fast, cloud-based)")
            except Exception as e:
                print(f"⚠️ Groq API not available: {str(e)}")
        
        # Fallback to OpenAI Whisper API
        if not self.use_groq and settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                self.use_openai = True
                print("✅ OpenAI Whisper API configured for STT (cloud-based)")
            except Exception as e:
                print(f"⚠️ OpenAI API not available: {str(e)}")
        
        if not self.use_groq and not self.use_openai:
            print("⚠️ No cloud STT API configured - will use MOCK mode")
            print("   Get free Groq API key: https://console.groq.com")
            print("   Or OpenAI API key: https://platform.openai.com")
    
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
        """Transcribe using Groq's Whisper API (free, very fast)."""
        file_size = os.path.getsize(audio_file_path)
        print(f"🎤 Transcribing with Groq API: {audio_file_path} ({file_size} bytes)")
        
        with open(audio_file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        # Determine MIME type from extension
        ext = os.path.splitext(audio_file_path)[1].lower()
        mime_map = {".wav": "audio/wav", ".mp3": "audio/mpeg", ".m4a": "audio/m4a",
                    ".webm": "audio/webm", ".ogg": "audio/ogg", ".mp4": "audio/mp4"}
        mime_type = mime_map.get(ext, "audio/wav")
        print(f"   File extension: {ext}, MIME type: {mime_type}")
        
        with open(audio_file_path, "rb") as audio_file:
            transcription = self.groq_client.audio.transcriptions.create(
                file=(os.path.basename(audio_file_path), audio_bytes, mime_type),
                model="whisper-large-v3",  # Most accurate model
                language=language,
                response_format="json"
            )
        
        transcribed_text = transcription.text.strip()
        print(f"✅ Groq transcription complete: {transcribed_text[:100]}...")
        
        return {
            "text": transcribed_text,
            "language": language,
            "method": "groq"
        }
    
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
