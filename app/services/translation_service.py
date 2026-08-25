"""
Translation service.
Handles bidirectional translation (Japanese ↔ English) with language detection.
"""

from typing import Optional, Literal
import warnings

# Suppress google.generativeai deprecation warning
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

from app.core.config import settings
from app.utils.language_detection import detect_language_from_text


class TranslationService:
    """
    Translation service for Japanese to English.
    Uses Gemini API or OpenAI for context-aware technical translation with fallback to mock mode.
    """
    
    def __init__(self):
        self.gemini_model = None
        self.groq_client = None
        self.use_gemini = False
        self.use_groq = False
        self.use_openai = False

        # ── Groq (primary — fast, free, 14k req/day with llama-3.1-8b-instant) ──
        if settings.GROQ_API_KEY:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
                self.use_groq = True
                print("✅ [Translation] Groq API initialized")
            except Exception as e:
                print(f"❌ [Translation] Groq init failed: {type(e).__name__}: {str(e)}")
                import traceback
                print(traceback.format_exc())
        else:
            print("⚠️ [Translation] GROQ_API_KEY not found in environment")

        # ── Gemini (secondary — always init independently so it's available as fallback) ──
        if settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel("gemini-2.5-flash")
                self.use_gemini = True
                print("✅ [Translation] Gemini API initialized")
            except Exception as e:
                print(f"❌ [Translation] Gemini init failed: {type(e).__name__}: {str(e)}")
        else:
            print("⚠️ [Translation] GEMINI_API_KEY not found in environment")

        if not self.use_groq and not self.use_gemini:
            print("❌ [Translation] NO APIs available - will use mock fallback")
    
    async def translate_technical_text(
        self,
        text: str,
        context: str = "technical support",
        source_language: str | None = None
    ) -> dict[str, str]:
        """
        Translate technical text with intelligent language detection.
        Handles both Japanese→English and English→Japanese.
        FAST: Uses Groq (primary) with Gemini fallback.
        
        Args:
            text: Source text to translate
            context: Context for translation (e.g., "technical support", "developer chat")
            source_language: Force source language ("ja" or "en"). If None, auto-detect.
        
        Returns:
            dict with:
                - translated_text: Translated text in target language
                - original_text: Original source text
                - source_language: Detected source language ("ja" or "en")
                - target_language: Target language ("en" or "ja")
                - method: Translation method used
        """
        
        # Auto-detect source language if not specified
        if source_language is None:
            source_language = detect_language_from_text(text)
        
        # If already in English and source is English, return as-is (no translation needed)
        if source_language == "en":
            return {
                "translated_text": text,
                "original_text": text,
                "source_language": "en",
                "target_language": "en",
                "method": "identity"
            }
        
        # Japanese → English translation
        target_language = "en"
        
        # Use Gemini 2.5-Flash directly for reliable translation (same as upload voice section)
        gemini_error = None
        if self.use_gemini:
            try:
                result = await self._gemini_translate(text, context, source_language, target_language)
                if result:
                    return result
            except Exception as e:
                gemini_error = (type(e).__name__, str(e))
                print(f"❌ GEMINI TRANSLATION FAILED: {type(e).__name__}: {str(e)}")
                import traceback
                print(traceback.format_exc())

        # Fallback: mock translation if Gemini fails
        print(f"⚠️ ⚠️ ⚠️ FALLING BACK TO MOCK - ALL TRANSLATION APIS FAILED")
        return self._mock_translate(text, context, source_language)
    
    async def _groq_translate(self, text: str, context: str, source_lang: str, target_lang: str) -> dict[str, str]:
        """Translate using Groq API (FAST)."""
        
        if not self.groq_client:
            raise RuntimeError("Groq client not initialized")
        
        try:
            # Build language-specific prompt
            if source_lang == "ja":
                system_msg = "You are a translator. Translate Japanese text to English."
                user_msg = text
            else:
                system_msg = "You are a translator."
                user_msg = text
            
            # Try multiple models in order of reliability
            models_to_try = [
                "meta-llama/llama-prompt-guard-2-86m",
                "meta-llama/llama-prompt-guard-2-22m",
            ]
            
            completion = None
            
            for model_name in models_to_try:
                try:
                    print(f"[DEBUG] Trying model: {model_name}")
                    completion = self.groq_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_msg},
                            {"role": "user", "content": user_msg}
                        ],
                        temperature=0.3,
                        max_tokens=512
                    )
                    print(f"[DEBUG] Model {model_name} succeeded!")
                    break
                except Exception as e:
                    print(f"[DEBUG] Model {model_name} failed: {type(e).__name__}: {str(e)[:200]}")
                    continue
            
            if not completion:
                raise RuntimeError("All Groq models failed")
            
            translated_text = completion.choices[0].message.content.strip()
            
            if not translated_text:
                raise ValueError("Groq returned empty translation")
            
            return {
                "translated_text": translated_text,
                "original_text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "method": "groq"
            }
        except Exception as e:
            import traceback
            raise
    
    async def _gemini_translate(self, text: str, context: str, source_lang: str, target_lang: str) -> dict[str, str]:
        """Translate using Gemini API (fallback when Groq fails)."""
        print(f"   [Translation] Gemini translating {source_lang}→{target_lang}...")
        
        if source_lang == "ja":
            prompt = f"""Translate this Japanese technical support message to English.
Output ONLY the English translation with NO explanations or extra text.

Japanese:
{text}"""
        else:
            prompt = f"""Translate to {target_lang}. Output ONLY the translation.

Text:
{text}"""
        
        response = self.gemini_model.generate_content(prompt)
        translated_text = response.text.strip()
        print(f"   ✅ [Translation] Gemini done: {translated_text[:80]}...")
        return {
            "translated_text": translated_text,
            "original_text": text,
            "source_language": source_lang,
            "target_language": target_lang,
            "method": "gemini"
        }

    async def _openai_translate(self, japanese_text: str, context: str) -> dict[str, str]:
        """Translate using OpenAI API."""
        print(f"🌐 Translating with OpenAI: {japanese_text[:50]}...")
        
        # System prompt for technical translation
        system_prompt = f"""You are a technical translator specializing in {context}.
Translate from Japanese to English with these requirements:
1. Preserve technical terminology accurately
2. Use clear, professional English
3. Maintain the original meaning and urgency
4. Format output as naturalEnglish for developers"""
        
        response = self.openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Translate this Japanese text to English:\n\n{japanese_text}"}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        translated_text = response.choices[0].message.content.strip()
        
        return {
            "translated_text": translated_text,
            "original_text": japanese_text,
            "method": "openai"
        }
    
    async def translate_to_japanese(self, english_text: str) -> dict[str, str]:
        """
        Translate English text to Japanese.
        Uses Gemini 2.5-Flash directly (same as upload voice section for consistency).
        """
        print(f"🌐 Translating EN→JA: {english_text[:50]}...")

        # Use Gemini 2.5-Flash directly (same as upload voice section)
        if self.use_gemini:
            try:
                prompt = f"""Translate this English text to Japanese. Output ONLY the Japanese translation, nothing else.

English: {english_text}"""
                response = self.gemini_model.generate_content(prompt)
                translated = response.text.strip()
                print(f"   ✅ EN→JA (Gemini): {translated[:40]}...")
                return {
                    "translated_text": translated,
                    "original_text": english_text,
                    "method": "gemini"
                }
            except Exception as e:
                print(f"   ⚠️ Gemini EN→JA failed: {type(e).__name__}: {str(e)[:100]}")
                import traceback
                print(traceback.format_exc())

        # Fallback: mock translation
        print(f"   ⚠️ All translation APIs failed - using mock fallback")
        return {
            "translated_text": f"[日本語訳] {english_text}",
            "original_text": english_text,
            "method": "mock"
        }

    def _mock_translate(self, text: str, context: str, source_lang: str) -> dict[str, str]:
        """
        Mock translation fallback - uses generic message.
        Works for ANY input when real APIs are unavailable.
        """
        if source_lang == "ja":
            translated_text = self._simple_translate_ja_to_en(text)
            target_lang = "en"
        else:
            # Shouldn't reach here, but handle anyway
            translated_text = text
            target_lang = source_lang
        
        print(f"🌐 MOCK Translation: {text[:50]}... → {translated_text[:50]}...")
        
        return {
            "translated_text": translated_text,
            "original_text": text,
            "source_language": source_lang,
            "target_language": target_lang,
            "method": "mock"
        }
    
    def _simple_translate_ja_to_en(self, text: str) -> str:
        """
        Simple Japanese to English fallback.
        Used when both Groq and Gemini fail.
        Attempts to extract key technical terms.
        """
        print(f"⚠️ Using fallback translation for: {text[:50]}...")
        
        # Map common Japanese technical terms to English
        ja_to_en_terms = {
            "サーバー": "server",
            "ダウン": "down",
            "エラー": "error",
            "接続": "connection",
            "ログイン": "login",
            "ログアウト": "logout",
            "データベース": "database",
            "API": "API",
            "パフォーマンス": "performance",
            "バックアップ": "backup",
            "セキュリティ": "security",
            "認証": "authentication",
        }
        
        # Simple term replacement fallback
        result = text
        for ja, en in ja_to_en_terms.items():
            if ja in text:
                result = result.replace(ja, en)
        
        # If no terms replaced, return generic message
        if result == text:
            return "Technical support request: Issue reported by developer. Please review the transcribed Japanese text below for specific details."
        return result


# Singleton instance
translation_service = TranslationService()
