"""
Translation service.
Handles Japanese to English translation with post-processing.
"""

from typing import Optional

from app.core.config import settings


class TranslationService:
    """
    Translation service for Japanese to English.
    Uses Gemini API or OpenAI for context-aware technical translation with fallback to mock mode.
    """
    
    def __init__(self):
        self.gemini_model = None
        self.use_gemini = False
        self.use_groq = False
        self.use_openai = False
        
        # Try Groq API first (since it's working for STT)
        if settings.GROQ_API_KEY:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
                self.use_groq = True
                print("✅ Groq API configured for translation")
            except Exception as e:
                print(f"⚠️ Groq API not available for translation: {str(e)}")
        
        # Try Gemini API as backup
        if not self.use_groq and settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.genai = genai
                self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
                self.use_gemini = True
                print("✅ Gemini API configured for translation (gemini-1.5-flash)")
            except Exception as e:
                print(f"⚠️ Gemini API not available: {str(e)}")
        
        # Fallback to OpenAI if available
        if not self.use_groq and not self.use_gemini and settings.OPENAI_API_KEY:
            try:
                import openai
                openai.api_key = settings.OPENAI_API_KEY
                self.openai = openai
                self.use_openai = True
                print("✅ OpenAI available for translation")
            except ImportError:
                print("⚠️ OpenAI not installed - will use MOCK mode")
        
        if not self.use_groq and not self.use_gemini and not self.use_openai:
            print("⚠️ No translation API available - using MOCK translation mode")
    
    async def translate_technical_text(
        self,
        japanese_text: str,
        context: str = "technical support"
    ) -> dict:
        """
        Translate Japanese text to English with technical context.
        FAST: Uses Groq (primary) with instant mock fallback.
        
        Args:
            japanese_text: Source Japanese text
            context: Context for translation (e.g., "technical support", "bug report")
        
        Returns:
            dict with:
                - translated_text: English translation
                - original_text: Original Japanese text
                - method: Translation method used
        """
        
        print(f"🌐 Translating: {japanese_text[:50]}...")
        
        # Try Groq API first (VERY FAST)
        if self.use_groq:
            try:
                return await self._groq_translate(japanese_text, context)
            except Exception as e:
                print(f"⚠️ Groq failed: {str(e)} - using mock")
        
        # Instant fallback to mock
        print("   ⚡ Using instant mock translation")
        return self._mock_translate(japanese_text, context)
    
    async def _groq_translate(self, japanese_text: str, context: str) -> dict:
        """Translate using Groq API (FAST)."""
        print(f"   Groq translating...")
        
        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "Translate Japanese to English. Output ONLY the translation."
                    },
                    {
                        "role": "user",
                        "content": japanese_text
                    }
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            translated_text = completion.choices[0].message.content.strip()
            
            print(f"   ✅ Groq done: {translated_text[:50]}...")
            
            return {
                "translated_text": translated_text,
                "original_text": japanese_text,
                "method": "groq"
            }
        except Exception as e:
            print(f"   ❌ Groq error: {str(e)}")
            raise
    
    async def _openai_translate(self, japanese_text: str, context: str) -> dict:
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
    
    async def translate_to_japanese(self, english_text: str) -> dict:
        """
        Translate English text to Japanese.
        Uses Groq (fast) with mock fallback.
        """
        print(f"🌐 Translating EN→JA: {english_text[:50]}...")

        if self.use_groq:
            try:
                completion = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": "Translate the following English text to Japanese. Output ONLY the Japanese translation, no explanations."
                        },
                        {
                            "role": "user",
                            "content": english_text
                        }
                    ],
                    temperature=0.1,
                    max_tokens=300
                )
                translated = completion.choices[0].message.content.strip()
                print(f"   ✅ EN→JA done: {translated[:40]}...")
                return {
                    "translated_text": translated,
                    "original_text": english_text,
                    "method": "groq"
                }
            except Exception as e:
                print(f"   ⚠️ Groq EN→JA failed: {e}")

        # Mock fallback
        return {
            "translated_text": f"[日本語訳] {english_text}",
            "original_text": english_text,
            "method": "mock"
        }

    def _mock_translate(self, japanese_text: str, context: str) -> dict:
        """
        Mock translation fallback - uses generic English message.
        Works for ANY Japanese input.
        """
        translated_text = self._simple_translate(japanese_text)
        
        print(f"🌐 MOCK Translation: {japanese_text[:50]}... → {translated_text[:50]}...")
        
        return {
            "translated_text": translated_text,
            "original_text": japanese_text,
            "method": "mock"
        }
    
    def _simple_translate(self, text: str) -> str:
        """
        Universal fallback for any Japanese text.
        Returns a generic professional English message.
        """
        print(f"⚠️ Using fallback translation for: {text[:50]}...")
        
        # For any Japanese text, return a professional generic message
        # This ensures the header always has English text
        return "Technical support request: Issue reported by developer. Please review the transcribed Japanese text below for specific details."


# Singleton instance
translation_service = TranslationService()
