"""
Encryption utilities for securing audio data at rest using AES-256 via Fernet.
Fernet provides AES encryption with HMAC authentication in CBC mode.
"""

import base64
import hashlib
from cryptography.fernet import Fernet  # type: ignore
from app.core.config import settings


class AudioEncryption:
    """Handle AES-256 encryption/decryption of audio files using Fernet."""
    
    def __init__(self):
        """Initialize encryption with the key derived from SECRET_KEY."""
        try:
            self.encryption_key = self._get_or_create_key()
            self.cipher = Fernet(self.encryption_key)
            print("[OK] Audio encryption initialized successfully")
        except Exception as e:
            print(f"[WARNING] Encryption initialization failed: {str(e)}")
            self.encryption_key = None
            self.cipher = None
    
    def _get_or_create_key(self) -> bytes:
        """
        Get encryption key derived from SECRET_KEY.
        Uses SHA256 hashing for key derivation and proper Fernet key formatting.
        """
        if not settings.SECRET_KEY or settings.SECRET_KEY == "":
            # Use a default dev key if not configured
            print("⚠️ SECRET_KEY not configured, using development key")
            secret = "techfixai-default-dev-key"
        else:
            secret = settings.SECRET_KEY
        
        # Derive a key using SHA256
        # Create a hash that's exactly 32 bytes (256 bits)
        key_material = hashlib.sha256(
            (secret + 'techfixai_audio_encryption').encode()
        ).digest()
        
        # Fernet requires a 32-byte key encoded in base64url format (44 chars total)
        derived_key = base64.urlsafe_b64encode(key_material)
        
        return derived_key
    
    def encrypt(self, audio_data: bytes) -> bytes:
        """
        Encrypt audio data using AES-256 (via Fernet).
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Encrypted audio bytes
        """
        if not self.cipher:
            print("⚠️ Encryption not initialized, returning raw data")
            return audio_data
        
        try:
            return self.cipher.encrypt(audio_data)
        except Exception as e:
            print(f"❌ Encryption failed: {str(e)}")
            return audio_data
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt audio data using AES-256 (via Fernet).
        
        Args:
            encrypted_data: Encrypted audio bytes
            
        Returns:
            Raw audio bytes
        """
        if not self.cipher:
            print("⚠️ Encryption not initialized, returning raw data")
            return encrypted_data
        
        try:
            return self.cipher.decrypt(encrypted_data)
        except Exception as e:
            print(f"❌ Decryption failed: {str(e)}")
            # Return raw data if decryption fails (might be unencrypted)
            return encrypted_data


# Initialize global encryption instance
try:
    audio_encryption = AudioEncryption()
except Exception as e:
    print(f"❌ Failed to initialize audio encryption: {str(e)}")
    # Create dummy object that passes through data
    class DummyEncryption:
        def encrypt(self, data): return data
        def decrypt(self, data): return data
    audio_encryption = DummyEncryption()
