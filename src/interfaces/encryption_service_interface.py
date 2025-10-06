"""
Interface para serviços de criptografia.

Define o contrato para criptografia e descriptografia de dados.
"""

from abc import ABC, abstractmethod


class IEncryptionService(ABC):
    """Interface para serviços de criptografia."""

    @abstractmethod
    def encrypt(self, data: str) -> bytes:
        """
        Criptografa uma string.

        Args:
            data: String a ser criptografada

        Returns:
            Bytes criptografados
        """
        pass

    @abstractmethod
    def decrypt(self, encrypted_data: bytes) -> str:
        """
        Descriptografa uma string criptografada.

        Args:
            encrypted_data: Bytes criptografados

        Returns:
            String original
        """
        pass
