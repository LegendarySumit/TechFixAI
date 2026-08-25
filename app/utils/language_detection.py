"""
Language detection utility for audio transcription.
Detects whether audio content is in English or Japanese.
"""

import re
from typing import Literal


def detect_language_from_text(text: str) -> Literal["en", "ja"]:
    """
    Detect language from text.
    
    Simple heuristic:
    - If text contains Japanese characters (Hiragana, Katakana, Kanji), assume Japanese
    - Otherwise assume English
    
    Args:
        text: Text to analyze
    
    Returns:
        "ja" for Japanese, "en" for English
    """
    if not text:
        return "en"
    
    # Japanese character ranges:
    # Hiragana: \u3040-\u309F
    # Katakana: \u30A0-\u30FF
    # Kanji: \u4E00-\u9FFF
    japanese_pattern = r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]'
    
    # Count Japanese characters
    japanese_chars = len(re.findall(japanese_pattern, text))
    total_chars = len(text)
    
    # If more than 10% of characters are Japanese, assume Japanese
    if total_chars > 0 and japanese_chars / total_chars > 0.1:
        return "ja"
    
    return "en"


def is_japanese_text(text: str) -> bool:
    """Check if text contains meaningful Japanese characters."""
    if not text:
        return False
    japanese_pattern = r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]'
    return bool(re.search(japanese_pattern, text))
