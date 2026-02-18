"""
Text utility functions.
"""

import re
from typing import Optional


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Input text
    
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, max_keywords: int = 5) -> list:
    """
    Extract basic keywords from text.
    Simple implementation - can be enhanced with NLP.
    
    Args:
        text: Input text
        max_keywords: Maximum number of keywords
    
    Returns:
        List of keywords
    """
    # Remove punctuation and convert to lowercase
    cleaned = re.sub(r'[^\w\s]', '', text.lower())
    
    # Split into words
    words = cleaned.split()
    
    # Remove common stop words (basic English list)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                  'of', 'with', 'is', 'was', 'are', 'were', 'be', 'been', 'being'}
    
    keywords = [word for word in words if word not in stop_words and len(word) > 3]
    
    # Return unique keywords (up to max)
    return list(dict.fromkeys(keywords))[:max_keywords]
