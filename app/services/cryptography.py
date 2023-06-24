from cryptography.fernet import Fernet

from app.settings.config import FERNET_KEY

_ENCODING = "utf-8"


def encrypt_key(email_key: str) -> str:
    f = Fernet(FERNET_KEY)
    encrypted_bytes = f.encrypt(bytes(email_key, _ENCODING))
    return encrypted_bytes.decode(_ENCODING)


def decrypt_key(code: str) -> str:
    f = Fernet(FERNET_KEY)
    decrypted_bytes = f.decrypt(bytes(code, _ENCODING))
    return decrypted_bytes.decode(_ENCODING)
