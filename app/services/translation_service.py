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
        
        Args:
            japanese_text: Source Japanese text
            context: Context for translation (e.g., "technical support", "bug report")
        
        Returns:
            dict with:
                - translated_text: English translation
                - original_text: Original Japanese text
                - method: Translation method used
        """
        
        # Try Groq API first
        if self.use_groq:
            try:
                return await self._groq_translate(japanese_text, context)
            except Exception as e:
                print(f"⚠️ Groq translation failed: {str(e)}, trying Gemini...")
        
        # Try Gemini API
        if self.use_gemini:
            try:
                return await self._gemini_translate(japanese_text, context)
            except Exception as e:
                print(f"⚠️ Gemini translation failed: {str(e)}, trying fallback...")
        
        # Fallback to OpenAI
        if self.use_openai:
            try:
                return await self._openai_translate(japanese_text, context)
            except Exception as e:
                print(f"⚠️ OpenAI translation failed: {str(e)}, using mock...")
        
        # Final fallback to mock
        return self._mock_translate(japanese_text, context)
    
    async def _groq_translate(self, japanese_text: str, context: str) -> dict:
        """Translate using Groq API with chat completion."""
        print(f"🌐 Translating with Groq API: {japanese_text[:50]}...")
        
        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Fast and accurate model
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator. Translate Japanese text to natural, fluent English. Output ONLY the English translation, no explanations or additional text."
                    },
                    {
                        "role": "user",
                        "content": f"Translate this Japanese text to English:\n\n{japanese_text}"
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            translated_text = completion.choices[0].message.content.strip()
            
            # Validate translation
            has_japanese = any('\u3040' <= char <= '\u309F' or  # Hiragana
                             '\u30A0' <= char <= '\u30FF' or  # Katakana  
                             '\u4E00' <= char <= '\u9FAF'     # Kanji
                             for char in translated_text)
            
            if has_japanese:
                raise Exception("Translation still contains Japanese characters")
            
            print(f"✅ Groq translation complete: {translated_text[:50]}...")
            
            return {
                "translated_text": translated_text,
                "original_text": japanese_text,
                "method": "groq"
            }
        except Exception as e:
            print(f"❌ Groq translation error: {str(e)}")
            raise
    
    async def _gemini_translate(self, japanese_text: str, context: str) -> dict:
        """Translate using Gemini API."""
        print(f"🌐 Translating with Gemini API: {japanese_text[:50]}...")
        
        try:
            prompt = f"""You are a professional translator. Translate the following Japanese text to natural, fluent English.

Requirements:
- Translate ONLY to English, do not include any Japanese text in your response
- Preserve the meaning and urgency of the original message
- Use clear, professional language
- Output ONLY the translated English text, no explanations or metadata

Japanese text:
{japanese_text}

English translation:"""
            
            response = self.gemini_model.generate_content(prompt)
            
            # Check if response is valid
            if not response or not response.text:
                raise Exception("Empty response from Gemini API")
            
            translated_text = response.text.strip()
            
            # Validate that translation actually happened (check if Japanese characters remain)
            has_japanese = any('\u3040' <= char <= '\u309F' or  # Hiragana
                             '\u30A0' <= char <= '\u30FF' or  # Katakana  
                             '\u4E00' <= char <= '\u9FAF'     # Kanji
                             for char in translated_text)
            
            if has_japanese:
                raise Exception("Translation still contains Japanese characters")
            
            print(f"✅ Gemini translation complete: {translated_text[:50]}...")
            
            return {
                "translated_text": translated_text,
                "original_text": japanese_text,
                "method": "gemini"
            }
        except Exception as e:
            print(f"❌ Gemini translation error: {str(e)}")
            raise  # Re-raise to trigger fallback
    
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
