"""
Serviço de criptografia implementando IEncryptionService.

Gerencia a criptografia e descriptografia de dados sensíveis.
"""

import os
import base64

from cryptography.fernet import Fernet
from dotenv import load_dotenv

from src.interfaces.encryption_service_interface import IEncryptionService
from src.utils.log import log

load_dotenv()


class EncryptionService(IEncryptionService):
    """Serviço de criptografia usando Fernet."""

    def __init__(self):
        """
        Inicializa o serviço de criptografia.

        Args:
            encryption_key: Chave de criptografia. Se None, busca em CHAVE_CRIPTOGRAFIA
        """
        chave = os.environ.get("CHAVE_CRIPTOGRAFIA")
        if not chave:
            log.error("CHAVE_CRIPTOGRAFIA não definida nas variáveis de ambiente.")
            raise ValueError("CHAVE_CRIPTOGRAFIA não definida.")

        # Garante que a chave está em formato base64 url-safe e tem 32 bytes
        try:
            # Se a chave não for 32 bytes, faz o padding e codifica
            if len(chave) != 44:  # 32 bytes base64 = 44 caracteres
                chave_bytes = chave.encode()
                chave_b64 = base64.urlsafe_b64encode(chave_bytes)
                if len(chave_b64) != 44:
                    log.error(
                        "CHAVE_CRIPTOGRAFIA inválida: deve ser 32 bytes codificados em base64 url-safe."
                    )
                    raise ValueError("CHAVE_CRIPTOGRAFIA inválida para Fernet.")
                self._key = chave_b64
            else:
                self._key = chave.encode()
            self._fernet = Fernet(self._key)
        except Exception as e:
            log.error(f"Erro ao inicializar Fernet: {e}")
            raise

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
