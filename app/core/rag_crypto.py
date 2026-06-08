import os
import hashlib
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv
from uuid import UUID

load_dotenv()

# MATCHING YOUR TECH STACK: Reusing your exact master variable name from the API Provider setup
MASTER_SECRET = os.getenv("ENCRYPTION_KEY")

if not MASTER_SECRET:
    raise RuntimeError("❌ Security Failure: ENCRYPTION_KEY is not set in your environment variables.")


def derive_workspace_key(workspace_id: UUID) -> bytes:
    """
    Mathematical Key Isolation: Blends your existing master ENCRYPTION_KEY 
    with the workspace UUID to create a localized 256-bit AES key.
    This guarantees that text and files from Workspace A can never be 
    decrypted by an exploit or leakage in Workspace B.
    """
    hasher = hashlib.sha256()
    hasher.update(MASTER_SECRET.encode("utf-8"))
    hasher.update(str(workspace_id).encode("utf-8"))
    return hasher.digest()


# =====================================================================
# TIER 1: BINARY FILE CRYPTOGRAPHY (For PostgreSQL Storage)
# =====================================================================

def encrypt_file_bytes(file_bytes: bytes, workspace_id: UUID) -> tuple[bytes, bytes]:
    """
    Encrypts raw file data blobs using high-security AES-256 GCM.
    Returns: a tuple of (ciphertext_bytes, random_iv_nonce_bytes)
    """
    key = derive_workspace_key(workspace_id)
    aesgcm = AESGCM(key)
    
    # FIX: Using os.urandom(12) to securely generate a 12-byte initialization vector (nonce)
    iv = os.urandom(12)
    
    # Encrypt raw data payload
    ciphertext = aesgcm.encrypt(iv, file_bytes, None)
    return ciphertext, iv


def decrypt_file_bytes(ciphertext: bytes, iv: bytes, workspace_id: UUID) -> bytes:
    """
    Decrypts encrypted file chunks retrieved from PostgreSQL.
    Returns: Raw unencrypted file bytes.
    """
    key = derive_workspace_key(workspace_id)
    aesgcm = AESGCM(key)
    
    # Decrypt and verify integrity tags on the fly
    return aesgcm.decrypt(iv, ciphertext, None)


# =====================================================================
# TIER 2: TEXT STRING CRYPTOGRAPHY (For ChromaDB Payload Masking)
# =====================================================================

def encrypt_text_string(plain_text: str, workspace_id: UUID) -> str:
    """
    Encrypts plain-text sentence chunks before pushing them into ChromaDB metadata.
    Returns: A URL-safe Base64 encoded ciphertext string.
    """
    if not plain_text or not plain_text.strip():
        return ""
        
    key = derive_workspace_key(workspace_id)
    aesgcm = AESGCM(key)
    
    # FIX: Using os.urandom(12) to securely generate a 12-byte initialization vector (nonce)
    iv = os.urandom(12)
    
    ciphertext = aesgcm.encrypt(iv, plain_text.encode("utf-8"), None)
    
    # Combine IV and Ciphertext together into one clean string package for ChromaDB string payload limits
    combined = iv + ciphertext
    return b64encode(combined).decode("utf-8")


def decrypt_text_string(encrypted_base64: str, workspace_id: UUID) -> str:
    """
    Decrypts the hidden ciphertext text chunks pulled from a ChromaDB search query vector package.
    Returns: The original human-readable plain text.
    """
    if not encrypted_base64:
        return ""
        
    key = derive_workspace_key(workspace_id)
    aesgcm = AESGCM(key)
    
    # Unpack combined package string back to original byte arrays
    combined_bytes = b64decode(encrypted_base64.encode("utf-8"))
    
    # Split the 12-byte random IV from the rest of the ciphertext bytes payload
    iv = combined_bytes[:12]
    ciphertext = combined_bytes[12:]
    
    decrypted_bytes = aesgcm.decrypt(iv, ciphertext, None)
    return decrypted_bytes.decode("utf-8")