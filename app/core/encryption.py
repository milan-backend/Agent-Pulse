import os
from cryptography.fernet import Fernet

# 🚨 In production, NEVER hardcode this. Always pull from a secure environment variable (.env)
# To generate a new master key for your .env file, open a python terminal and run: 
# from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())
MASTER_KEY = os.environ.get("AGENTPULSE_VAULT_KEY") 

def get_cipher():
    if not MASTER_KEY:
        raise ValueError("AGENTPULSE_VAULT_KEY environment variable is not set!")
    return Fernet(MASTER_KEY.encode())

def encrypt_vault_secret(plain_text: str) -> str:
    """Encrypts a plaintext string (like a database password) before saving to the Vault."""
    cipher_suite = get_cipher()
    
    # Fernet requires bytes, so we encode the string, encrypt it, and decode back to a string
    encrypted_bytes = cipher_suite.encrypt(plain_text.encode('utf-8'))
    return encrypted_bytes.decode('utf-8')

def decrypt_vault_secret(encrypted_text: str) -> str:
    """Decrypts a secure string from the Vault back into plaintext."""
    cipher_suite = get_cipher()
    
    # Decrypt the ciphertext and decode it back into readable text
    decrypted_bytes = cipher_suite.decrypt(encrypted_text.encode('utf-8'))
    return decrypted_bytes.decode('utf-8')