import secrets
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# 🔐 Generate API key
def generate_api_key():
    key_id = secrets.token_hex(4)  # short lookup id
    secret = secrets.token_urlsafe(32)

    api_key = f"{key_id}.{secret}"

    return api_key, key_id


# 🔒 Hash API key
def hash_api_key(api_key: str):
    return pwd_context.hash(api_key)


# ✅ Verify API key
def verify_api_key(
    plain_key: str,
    hashed_key: str
):
    return pwd_context.verify(
        plain_key,
        hashed_key
    )

# 🔐 Hash password
def hash_password(password: str):
    return pwd_context.hash(password)


# ✅ Verify password
def verify_password(
    plain_password: str,
    hashed_password: str
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )