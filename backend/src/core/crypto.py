from cryptography.fernet import Fernet, InvalidToken

from core.config import get_settings
from core.exceptions import AppError


class CryptoService:
    """Cifrado en reposo para tokens OAuth de Mercado Pago (regla D3)."""

    def __init__(self) -> None:
        key = get_settings().fernet_key
        if not key:
            self._fernet: Fernet | None = None
        else:
            self._fernet = Fernet(key.encode() if isinstance(key, str) else key)

    def encrypt(self, plaintext: str) -> str:
        if self._fernet is None:
            raise AppError("FERNET_KEY not configured", code="crypto_unconfigured")
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        if self._fernet is None:
            raise AppError("FERNET_KEY not configured", code="crypto_unconfigured")
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except InvalidToken as exc:
            raise AppError("Invalid ciphertext", code="crypto_invalid") from exc
