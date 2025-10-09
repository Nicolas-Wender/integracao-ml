"""
Interface para serviços de criptografia.

Define o contrato para criptografia e descriptografia de dados.
"""

from abc import ABC, abstractmethod


class IEncryptionService(ABC):
    """Interface para serviços de criptografia."""

    @abstractmethod
    def encrypt(self, data: str) -> str:
        """
        Criptografa uma string.

        Args:
            data: String a ser criptografada

        Returns:
            Texto criptografado em base64 compatível com CryptoJS
        """
        pass

    @abstractmethod
    def decrypt(self, encrypted_data: str) -> str:
        """
        Descriptografa uma string criptografada.

        Args:
            encrypted_data: Texto criptografado em base64

        Returns:
            String original
        """
        pass
