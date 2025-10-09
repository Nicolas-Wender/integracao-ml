"""Serviço de criptografia compatível com CryptoJS AES."""

from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass
from typing import Tuple, Union

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from dotenv import load_dotenv

from src.interfaces.encryption_service_interface import IEncryptionService
from src.utils.log import log

load_dotenv()

PKCS7_BLOCK_SIZE = 128


@dataclass(frozen=True)
class _CryptoConfig:
    key_bytes: bytes
    key_length: int = 32  # AES-256
    iv_length: int = 16
    salt_size: int = 8


class EncryptionService(IEncryptionService):
    """Serviço de criptografia usando AES/CBC com derivação EVP_BytesToKey."""

    def __init__(self) -> None:
        chave = os.environ.get("ENCRYPTION_KEY")
        if not chave:
            log.error("ENCRYPTION_KEY não definida nas variáveis de ambiente.")
            raise ValueError("ENCRYPTION_KEY não definida.")

        self._config = _CryptoConfig(key_bytes=chave.encode("utf-8"))

    def encrypt(self, data: str) -> str:
        """Aplica AES-256-CBC com padding PKCS7, compatível com CryptoJS."""
        try:
            if not data:
                return ""

            salt = os.urandom(self._config.salt_size)
            key, iv = self._derive_key_iv(salt)

            padder = padding.PKCS7(PKCS7_BLOCK_SIZE).padder()
            padded = padder.update(data.encode("utf-8")) + padder.finalize()

            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded) + encryptor.finalize()

            payload = b"Salted__" + salt + ciphertext
            return base64.b64encode(payload).decode("utf-8")

        except Exception as exc:  # pragma: no cover - log and rethrow
            log.error(f"Erro ao criptografar dados: {exc}")
            raise

    def decrypt(self, encrypted_data: Union[str, bytes]) -> str:
        """Reverte o processo de criptografia, retornando o texto original."""
        try:
            if not encrypted_data:
                return ""

            if isinstance(encrypted_data, bytes):
                encrypted_data = encrypted_data.decode("utf-8")

            raw = base64.b64decode(encrypted_data)
            if not raw.startswith(b"Salted__") or len(raw) <= 16:
                raise ValueError("Formato de payload inválido para descriptografia.")

            salt = raw[8:16]
            ciphertext = raw[16:]

            key, iv = self._derive_key_iv(salt)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            unpadder = padding.PKCS7(PKCS7_BLOCK_SIZE).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

            return plaintext.decode("utf-8")

        except Exception as exc:  # pragma: no cover - log and rethrow
            log.error(f"Erro ao descriptografar dados: {exc}")
            raise

    def encrypt_password(self, text: str) -> str:
        """Alias para criptografia de senhas (mantém paridade com CryptoJS)."""
        return self.encrypt(text)

    def decrypt_password(self, encrypted_text: Union[str, bytes]) -> str:
        """Alias para descriptografia de senhas."""
        return self.decrypt(encrypted_text)

    def generate_token(self) -> str:
        """Gera token randômico em hexadecimal (32 bytes)."""
        return os.urandom(32).hex()

    @staticmethod
    def hash_token(token: str) -> str:
        """Retorna o hash SHA-256 do token em hexadecimal."""
        if not token:
            return ""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _derive_key_iv(self, salt: bytes) -> Tuple[bytes, bytes]:
        """Replica o algoritmo EVP_BytesToKey (MD5) utilizado pelo CryptoJS."""
        key_material = b""
        last_block = b""

        while len(key_material) < (self._config.key_length + self._config.iv_length):
            last_block = hashlib.md5(
                last_block + self._config.key_bytes + salt
            ).digest()
            key_material += last_block

        key = key_material[: self._config.key_length]
        iv = key_material[
            self._config.key_length : self._config.key_length + self._config.iv_length
        ]
        return key, iv
