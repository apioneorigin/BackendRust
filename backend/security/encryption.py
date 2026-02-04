"""
Encryption Module - AES-256-GCM encryption, HMAC, secure tokens.
"""

import base64
import hashlib
import hmac
import os
import re
import secrets
from typing import Any, Optional

# Cryptography library status - lazy loaded
# We don't import at module load to avoid issues with broken cryptography installs
_crypto_checked = False
_crypto_available = False


def _check_cryptography():
    """Check if cryptography library is available (lazy check)."""
    global _crypto_checked, _crypto_available
    if _crypto_checked:
        return _crypto_available

    _crypto_checked = True
    try:
        # Use importlib to avoid direct import issues
        import importlib
        crypto = importlib.import_module('cryptography.hazmat.primitives.ciphers.aead')
        _crypto_available = hasattr(crypto, 'AESGCM')
    except Exception:
        _crypto_available = False

    return _crypto_available


def _get_aesgcm():
    """Get AESGCM class if available."""
    if not _check_cryptography():
        return None
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        return AESGCM
    except Exception:
        return None


def _get_pbkdf2():
    """Get PBKDF2HMAC class if available."""
    if not _check_cryptography():
        return None
    try:
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.backends import default_backend
        return PBKDF2HMAC, hashes, default_backend
    except Exception:
        return None


# Configuration
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
HMAC_SECRET = os.getenv("HMAC_SECRET", os.getenv("JWT_SECRET", ""))
PBKDF2_ITERATIONS = 100_000
AES_KEY_SIZE = 32  # 256 bits
NONCE_SIZE = 12  # 96 bits for GCM


def _derive_key_stdlib(password: bytes, salt: bytes) -> bytes:
    """Derive a key using PBKDF2 from stdlib (fallback)."""
    return hashlib.pbkdf2_hmac(
        'sha256',
        password,
        salt,
        PBKDF2_ITERATIONS,
        dklen=AES_KEY_SIZE
    )


def _derive_key_crypto(password: bytes, salt: bytes) -> bytes:
    """Derive a key using PBKDF2 from cryptography library."""
    result = _get_pbkdf2()
    if not result:
        return _derive_key_stdlib(password, salt)
    PBKDF2HMAC, hashes, default_backend = result
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=AES_KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(password)


def _derive_key(password: bytes, salt: bytes) -> bytes:
    """Derive a key using PBKDF2."""
    if _check_cryptography():
        return _derive_key_crypto(password, salt)
    return _derive_key_stdlib(password, salt)


def _get_encryption_key() -> bytes:
    """Get or derive the encryption key."""
    if not ENCRYPTION_KEY:
        # In production, this should fail
        if os.getenv("ENVIRONMENT") == "production":
            raise ValueError("ENCRYPTION_KEY must be set in production")
        # Development fallback - derive from JWT_SECRET
        jwt_secret = os.getenv("JWT_SECRET", "dev-secret-key")
        return _derive_key(jwt_secret.encode(), b"encryption-salt")

    # If key is provided, derive from it
    return _derive_key(ENCRYPTION_KEY.encode(), b"encryption-salt")


def encrypt_data(plaintext: str, associated_data: Optional[bytes] = None) -> str:
    """
    Encrypt data using AES-256-GCM.
    Returns base64-encoded ciphertext with nonce prepended.
    Falls back to base64 encoding with HMAC if cryptography not available.
    """
    AESGCM = _get_aesgcm()
    if not AESGCM:
        # Fallback: base64 encode with HMAC signature
        # NOT secure encryption, but provides integrity checking
        encoded = base64.urlsafe_b64encode(plaintext.encode()).decode()
        sig = create_hmac(encoded)
        return f"{encoded}.{sig}"

    key = _get_encryption_key()
    aesgcm = AESGCM(key)

    nonce = secrets.token_bytes(NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), associated_data)

    # Prepend nonce to ciphertext
    combined = nonce + ciphertext
    return base64.urlsafe_b64encode(combined).decode()


def decrypt_data(encrypted: str, associated_data: Optional[bytes] = None) -> str:
    """
    Decrypt AES-256-GCM encrypted data.
    """
    AESGCM = _get_aesgcm()
    if not AESGCM:
        # Fallback: verify HMAC and decode
        if "." in encrypted:
            encoded, sig = encrypted.rsplit(".", 1)
            if verify_hmac(encoded, sig):
                return base64.urlsafe_b64decode(encoded.encode()).decode()
        raise ValueError("Invalid encrypted data or signature mismatch")

    key = _get_encryption_key()
    aesgcm = AESGCM(key)

    combined = base64.urlsafe_b64decode(encrypted.encode())
    nonce = combined[:NONCE_SIZE]
    ciphertext = combined[NONCE_SIZE:]

    plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data)
    return plaintext.decode()


def hash_data(data: str, salt: Optional[str] = None) -> str:
    """
    Hash data using SHA-256.
    Optionally with a salt.
    """
    if salt:
        data = salt + data
    return hashlib.sha256(data.encode()).hexdigest()


def create_hmac(data: str, secret: Optional[str] = None) -> str:
    """Create HMAC-SHA256 signature."""
    key = (secret or HMAC_SECRET).encode()
    return hmac.new(key, data.encode(), hashlib.sha256).hexdigest()


def verify_hmac(data: str, signature: str, secret: Optional[str] = None) -> bool:
    """Verify HMAC-SHA256 signature using timing-safe comparison."""
    expected = create_hmac(data, secret)
    return hmac.compare_digest(expected, signature)


def verify_hash(data: str, hashed: str, salt: Optional[str] = None) -> bool:
    """Verify a hash using timing-safe comparison."""
    computed = hash_data(data, salt)
    return hmac.compare_digest(computed, hashed)


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def generate_api_key(prefix: str = "sk") -> str:
    """Generate an API key with prefix."""
    token = secrets.token_urlsafe(32)
    return f"{prefix}_{token}"


def mask_email(email: str) -> str:
    """Mask an email address."""
    if not email or "@" not in email:
        return email

    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]

    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """Mask a phone number, showing only last 4 digits."""
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 4:
        return "*" * len(phone)
    return "*" * (len(digits) - 4) + digits[-4:]


def mask_credit_card(card: str) -> str:
    """Mask a credit card number, showing only last 4 digits."""
    digits = re.sub(r"\D", "", card)
    if len(digits) < 4:
        return "*" * len(card)
    return "*" * (len(digits) - 4) + digits[-4:]


def mask_ssn(ssn: str) -> str:
    """Mask an SSN."""
    digits = re.sub(r"\D", "", ssn)
    if len(digits) < 4:
        return "*" * len(ssn)
    return "***-**-" + digits[-4:]


def mask_sensitive_data(value: str, data_type: str = "auto") -> str:
    """
    Mask sensitive data based on type.
    Auto-detects type if not specified.
    """
    if data_type == "auto":
        # Auto-detect
        if "@" in value:
            return mask_email(value)
        elif re.match(r"^\+?[\d\s\-()]+$", value) and len(re.sub(r"\D", "", value)) >= 10:
            return mask_phone(value)
        elif re.match(r"^[\d\s\-]+$", value) and len(re.sub(r"\D", "", value)) in (15, 16):
            return mask_credit_card(value)
        elif re.match(r"^\d{3}-?\d{2}-?\d{4}$", value):
            return mask_ssn(value)
        else:
            # Generic masking - show first and last char
            if len(value) <= 4:
                return "*" * len(value)
            return value[0] + "*" * (len(value) - 2) + value[-1]

    if data_type == "email":
        return mask_email(value)
    elif data_type == "phone":
        return mask_phone(value)
    elif data_type == "credit_card":
        return mask_credit_card(value)
    elif data_type == "ssn":
        return mask_ssn(value)
    else:
        return "*" * len(value)


def encrypt_field(value: Any, field_name: str) -> str:
    """Encrypt a field with associated data (field name) for integrity."""
    return encrypt_data(str(value), field_name.encode())


def decrypt_field(encrypted: str, field_name: str) -> str:
    """Decrypt a field with associated data verification."""
    return decrypt_data(encrypted, field_name.encode())


def encrypt_dict_fields(
    data: dict[str, Any],
    fields_to_encrypt: set[str]
) -> dict[str, Any]:
    """Encrypt specific fields in a dictionary."""
    result = data.copy()
    for field in fields_to_encrypt:
        if field in result and result[field] is not None:
            result[field] = encrypt_field(result[field], field)
    return result


def decrypt_dict_fields(
    data: dict[str, Any],
    fields_to_decrypt: set[str]
) -> dict[str, Any]:
    """Decrypt specific fields in a dictionary."""
    result = data.copy()
    for field in fields_to_decrypt:
        if field in result and result[field] is not None:
            try:
                result[field] = decrypt_field(result[field], field)
            except Exception:
                # Field may not be encrypted
                pass
    return result
