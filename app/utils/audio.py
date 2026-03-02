"""
Audio utility functions.
"""

import os
from typing import Optional


def get_audio_duration(file_path: str) -> Optional[float]:
    """
    Get audio file duration in seconds.
    
    Args:
        file_path: Path to audio file
    
    Returns:
        Duration in seconds or None if unable to determine
    """
    try:
        import wave
        import contextlib

        with contextlib.closing(wave.open(file_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration
    except Exception:
        # For non-WAV files or errors, return None
        # Can be extended with other libraries (e.g., pydub)
        return None


def validate_audio_file(file_path: str) -> bool:
    """
    Validate that file exists and is a valid audio file.
    
    Args:
        file_path: Path to audio file
    
    Returns:
        True if valid, False otherwise
    """
    if not os.path.exists(file_path):
        return False
    
    # Check file size (not empty and not too large)
    file_size = os.path.getsize(file_path)
    if file_size == 0 or file_size > 100 * 1024 * 1024:  # 100MB max
        return False
    
    # Check extension
    valid_extensions = ['.wav', '.mp3', '.m4a', '.webm', '.ogg']
    _, ext = os.path.splitext(file_path)
    
    return ext.lower() in valid_extensions
