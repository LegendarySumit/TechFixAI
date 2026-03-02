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
                print("✅ [Translation] Groq API ready (llama-3.1-8b-instant)")
            except Exception as e:
                print(f"⚠️ [Translation] Groq init failed: {str(e)}")
        else:
            print("⚠️ [Translation] GROQ_API_KEY not set — Groq disabled")

        # ── Gemini (secondary — always init independently so it's available as fallback) ──
        if settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
                self.use_gemini = True
                print("✅ [Translation] Gemini API ready (gemini-1.5-flash) — fallback")
            except Exception as e:
                print(f"⚠️ [Translation] Gemini init failed: {str(e)}")
        else:
            print("⚠️ [Translation] GEMINI_API_KEY not set — Gemini disabled")

        if not self.use_groq and not self.use_gemini:
            print("❌ [Translation] NO real API available — will use MOCK mode!")
    
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
        
        # 1️⃣ Try Groq first (fast)
        if self.use_groq:
            try:
                return await self._groq_translate(japanese_text, context)
            except Exception as e:
                import traceback
                print(f"❌ [Translation] Groq failed: {type(e).__name__}: {str(e)}")
                print(traceback.format_exc())

        # 2️⃣ Try Gemini as real fallback
        if self.use_gemini:
            try:
                return await self._gemini_translate(japanese_text, context)
            except Exception as e:
                import traceback
                print(f"❌ [Translation] Gemini failed: {type(e).__name__}: {str(e)}")
                print(traceback.format_exc())

        # 3️⃣ Emergency mock fallback
        print("⚠️⚠️⚠️ FALLING BACK TO MOCK TRANSLATION — both Groq and Gemini failed")
        return self._mock_translate(japanese_text, context)
    
    async def _groq_translate(self, japanese_text: str, context: str) -> dict:
        """Translate using Groq API (FAST)."""
        print(f"   Groq translating...")
        
        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",  # 14,400 req/day free vs 30/day for 70b
                messages=[
                    {
                        "role": "system",
                        "content": "Translate Japanese to English. Output ONLY the English translation, nothing else."
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
    
    async def _gemini_translate(self, japanese_text: str, context: str) -> dict:
        """Translate using Gemini API (fallback when Groq fails)."""
        print(f"   [Translation] Gemini translating...")
        prompt = f"""Translate this Japanese technical support message to English.
Output ONLY the English translation, nothing else.

Japanese:
{japanese_text}"""
        response = self.gemini_model.generate_content(prompt)
        translated_text = response.text.strip()
        print(f"   ✅ [Translation] Gemini done: {translated_text[:80]}...")
        return {
            "translated_text": translated_text,
            "original_text": japanese_text,
            "method": "gemini"
        }

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
                    model="llama-3.1-8b-instant",
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
