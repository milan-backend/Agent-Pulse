import os
from cryptography.fernet import Fernet
from typing import Optional

# Fetch the Application's Master Encryption Key from your .env file
# This key must remain secret. If a hacker doesn't have this key, 
# the database strings are completely useless to them.
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    # Fallback to generate a temporary token so your app doesn't crash during local tests.
    # CRITICAL: For production, you will generate one and paste it into Render's Env variables!
    print("[Warning] ENCRYPTION_KEY not found in environment. Generating a temporary secret key token...")
    ENCRYPTION_KEY = Fernet.generate_key().decode()

fernet_client = Fernet(ENCRYPTION_KEY.encode())


def encrypt_api_key(raw_key: str) -> str:
    """
    Takes a plain text user API key string and converts it into 
    an encrypted, unreadable AES-256 ciphertext string.
    """
    if not raw_key:
        raise ValueError("Cannot encrypt an empty API key string.")
    return fernet_client.encrypt(raw_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Takes the encrypted ciphertext string from PostgreSQL and 
    decrypts it back into plain text for the temporary execution memory.
    """
    if not encrypted_key:
        raise ValueError("Cannot decrypt an empty ciphertext string.")
    return fernet_client.decrypt(encrypted_key.encode()).decode()