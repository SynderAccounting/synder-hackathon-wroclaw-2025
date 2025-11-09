import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Get encryption key from environment or generate one
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'demo-key-change-in-production-please-use-secure-key')

def _get_fernet():
    """Create Fernet cipher from key"""
    # Derive a proper key from the passphrase
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'static_salt_for_demo',  # In production, use unique salt per installation
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(ENCRYPTION_KEY.encode()))
    return Fernet(key)

def encrypt(plaintext: str) -> str:
    """Encrypt plaintext string"""
    if not plaintext:
        return ''
    f = _get_fernet()
    encrypted = f.encrypt(plaintext.encode())
    return base64.urlsafe_b64encode(encrypted).decode()

def decrypt(ciphertext: str) -> str:
    """Decrypt ciphertext string"""
    if not ciphertext:
        return ''
    f = _get_fernet()
    decoded = base64.urlsafe_b64decode(ciphertext.encode())
    decrypted = f.decrypt(decoded)
    return decrypted.decode()
