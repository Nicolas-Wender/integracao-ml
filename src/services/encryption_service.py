"""
Serviço de criptografia implementando IEncryptionService.

Gerencia a criptografia e descriptografia de dados sensíveis.
"""

import os

from cryptography.fernet import Fernet

from src.interfaces.encryption_service_interface import IEncryptionService
from src.utils.log import log


class EncryptionService(IEncryptionService):
    """Serviço de criptografia usando Fernet."""

    def __init__(self):
        """
        Inicializa o serviço de criptografia.

        Args:
            encryption_key: Chave de criptografia. Se None, busca em CHAVE_CRIPTOGRAFIA
        """
        self._key = str(os.environ.get("CHAVE_CRIPTOGRAFIA")).encode()
        self._fernet = Fernet(self._key)

    def encrypt(self, data: str) -> bytes:
        """
        Criptografa uma string.

        Args:
            data: String a ser criptografada

        Returns:
            String criptografada em base64
        """
        try:
            if not data:
                return b""

            return self._fernet.encrypt(data.encode())

        except Exception as e:
            log.error(f"Erro ao criptografar dados: {e}")
            raise

    def decrypt(self, encrypted_data: str) -> str:
        """
        Descriptografa uma string.

        Args:
            encrypted_data: String criptografada em base64

        Returns:
            String original descriptografada
        """
        try:
            if not encrypted_data:
                return encrypted_data

            return self._fernet.decrypt(encrypted_data).decode()

        except Exception as e:
            log.error(f"Erro ao descriptografar dados: {e}")
            raise
