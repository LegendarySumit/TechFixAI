"""
Real-time transcription confidence scoring using Gemini API.
Analyzes transcribed text quality and accuracy.
"""

import json
from typing import Dict, Optional, Any
from app.core.config import settings


class ConfidenceService:
    """
    Uses Gemini API to assess transcription quality in real-time.
    Provides accurate confidence scores based on text analysis.
    """
    
    def __init__(self):
        self.gemini_client = None
        self.use_gemini = False
        
        if settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_client = genai
                self.use_gemini = True
                print("✅ Gemini API INITIALIZED - Real-time confidence scoring READY")
            except Exception as e:
                print(f"❌ Gemini API initialization failed: {str(e)}")
                print("   Install: pip install google-generativeai")
        else:
            print("⚠️ GEMINI_API_KEY not set in environment - will use heuristic analysis")

    
    async def calculate_real_confidence(
        self,
        transcribed_text: str,
        language: str = "Japanese"
    ) -> Dict[str, Any]:
        """
        Calculate transcription confidence using Gemini AI analysis.
        
        Args:
            transcribed_text: The transcribed text to analyze
            language: Original language of audio (default: Japanese)
        
        Returns:
            Dictionary with:
                - confidence: Score 0.0-1.0 (1.0 = 100% accurate)
                - quality_status: 'high', 'medium', or 'low'
                - reason: Explanation of confidence score
                - details: Technical analysis details
        """
        
        if not transcribed_text or not transcribed_text.strip():
            return {
                "confidence": 0.0,
                "quality_status": "low",
                "reason": "Empty transcription",
                "details": "No text to analyze"
            }
        
        # Use Gemini - ALWAYS! Never fallback
        if self.use_gemini:
            try:
                return await self._gemini_analyze(transcribed_text, language)
            except Exception as e:
                print(f"❌ Gemini analysis failed: {str(e)}")
                # RETRY once before giving up
                try:
                    print("   🔄 Retrying Gemini analysis...")
                    return await self._gemini_analyze(transcribed_text, language)
                except Exception as retry_error:
                    print(f"❌ Gemini retry failed: {str(retry_error)}")
                    # Only fallback if Gemini fails twice
                    print("   ⚠️ Falling back to heuristic analysis...")
                    return self._heuristic_analyze(transcribed_text)
        else:
            print("⚠️ Gemini API not available - using heuristic analysis")
            return self._heuristic_analyze(transcribed_text)
    
    async def _gemini_analyze(self, text: str, language: str) -> Dict[str, Any]:
        """Analyze text quality using Gemini API."""
        try:
            model = self.gemini_client.GenerativeModel('gemini-pro')
            
            prompt = f"""You are a transcription quality analyzer. Analyze this {language} technical support transcription for quality and accuracy.

Transcribed Text:
"{text}"

IMPORTANT: Return ONLY valid JSON, no markdown formatting, no code blocks, no extra text.

{{
    "is_coherent": true or false,
    "is_technical": true or false,
    "is_complete": true or false,
    "confidence_percentage": number between 0 and 100,
    "issues": ["issue1", "issue2"],
    "quality_assessment": "Excellent" or "Good" or "Fair" or "Poor"
}}

Guidelines for confidence_percentage:
- 95-100: Perfect transcription, exactly matches what would be said
- 85-94: Very good transcription, minor word variations only
- 75-84: Good transcription, some words may be unclear but meaning is clear
- 60-74: Fair transcription, several errors but main meaning comprehensible
- Below 60: Poor transcription, significant errors make it hard to understand

Return the JSON immediately with no explanations."""
            
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            print(f"   📝 Gemini Response: {response_text[:100]}...")
            
            # Parse JSON from response
            import re
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            
            # Find JSON object
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                analysis = json.loads(json_str)
            else:
                analysis = json.loads(response_text)
            
            confidence = analysis.get("confidence_percentage", 50) / 100.0
            quality = analysis.get("quality_assessment", "Fair")
            
            # Validate confidence is not stuck at default
            if confidence <= 0 or confidence > 1.0:
                raise ValueError(f"Invalid confidence value: {confidence}")
            
            # Map quality assessment to status
            if quality in ["Excellent", "Perfect", "excellent"]:
                quality_status = "high"
            elif quality in ["Good", "good"]:
                quality_status = "medium"
            elif quality in ["Fair", "fair"]:
                quality_status = "medium"
            else:
                quality_status = "low"
            
            issues = analysis.get("issues", [])
            raw_percentage = analysis.get("confidence_percentage", 50)
            reason = f"Gemini AI confidence: {raw_percentage}%"
            if issues:
                reason += f" - Issues: {', '.join(issues[:2])}"
            
            return {
                "confidence": min(max(confidence, 0.0), 1.0),
                "quality_status": quality_status,
                "reason": reason,
                "details": {
                    "is_coherent": analysis.get("is_coherent"),
                    "is_technical": analysis.get("is_technical"),
                    "is_complete": analysis.get("is_complete"),
                    "issues": issues,
                    "raw_percentage": raw_percentage,
                    "method": "gemini"
                }
            }
        
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error from Gemini: {str(e)}")
            print(f"   Response was: {response_text[:200]}")
            raise ValueError(f"Gemini returned invalid JSON: {str(e)}")
        except Exception as e:
            print(f"❌ Gemini analysis error: {str(e)}")
            raise
    
    def _heuristic_analyze(self, text: str) -> Dict[str, any]:
        """
        Fallback heuristic analysis when Gemini is not available.
        Format:confidence based on text characteristics.
        """
        
        if not text or len(text.strip()) == 0:
            return {
                "confidence": 0.0,
                "quality_status": "low",
                "reason": "Empty text",
                "details": {}
            }
        
        # Clean text
        text = text.strip()
        
        # Analyze characteristics
        coherence_score = 0.0
        
        # Length check (longer = more likely to be accurate)
        length_score = min(len(text) / 100, 1.0)  # Good at 100+ chars
        coherence_score += length_score * 0.3
        
        # Punctuation check (proper punctuation = better quality)
        has_punctuation = any(p in text for p in '.!?,;:')
        punctuation_score = 1.0 if has_punctuation else 0.5
        coherence_score += punctuation_score * 0.25
        
        # Word count (more words = more content = higher confidence)
        words = text.split()
        word_count_score = min(len(words) / 20, 1.0)  # Good at 20+ words
        coherence_score += word_count_score * 0.2
        
        # Uniqueness (diverse vocabulary)
        unique_words = len(set(words))
        diversity_score = min(unique_words / max(len(words) * 0.6, 5), 1.0)
        coherence_score += diversity_score * 0.15
        
        # Technical terms detection
        technical_keywords = [
            'server', 'database', 'api', 'error', 'timeout', 'crash', 'bug',
            'password', 'login', 'authentication', 'ssl', 'port', 'port',
            'cpu', 'memory', 'disk', 'bandwidth', 'latency', 'クラッシュ',
            'エラー', 'サーバー', 'データベース', 'ログイン'
        ]
        has_technical = any(term in text.lower() for term in technical_keywords)
        
        if has_technical:
            coherence_score += 0.1
        
        # Normalize to 0.0-1.0
        final_confidence = min(max(coherence_score, 0.0), 1.0)
        
        # Map to quality status
        if final_confidence >= 0.85:
            quality_status = "high"
        elif final_confidence >= 0.70:
            quality_status = "medium"
        else:
            quality_status = "low"
        
        reason = f"Heuristic analysis: {int(final_confidence * 100)}% confidence"
        
        return {
            "confidence": final_confidence,
            "quality_status": quality_status,
            "reason": reason,
            "details": {
                "length": len(text),
                "word_count": len(words),
                "has_punctuation": has_punctuation,
                "has_technical_terms": has_technical,
                "analysis_method": "heuristic"
            }
        }


# Singleton instance
confidence_service = ConfidenceService()
