"""
Interface para repositório de credenciais.

Define o contrato para persistência de credenciais.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ICredentialsRepository(ABC):
    """Interface para repositório de credenciais."""

    @abstractmethod
    def get_credentials(self, id: str) -> Dict[str, Any]:
        """
        Obtém as credenciais da loja pelo identificador.

        Args:
            id: Identificador da loja
        Returns:
            DataFrame com as credenciais
        """
        pass

    @abstractmethod
    def save_token(self, id: str, token: Dict[str, Any]) -> None:
        """
        Salva o token para a loja especificada.

        Args:
            id: Identificador da loja
            token: Dados do token (access_token, refresh_token, validade)
        """
        pass

    @abstractmethod
    def get_refresh_payload(self, id: str) -> Dict[str, Any]:
        """
        Obtém o payload necessário para refresh do token.

        Args:
            id: Identificador da loja
        Returns:
            Dicionário com o payload para refresh
        """
        pass

    @abstractmethod
    def clear_tokens(self, id: str) -> None:
        """
        Limpa os tokens da loja pelo identificador.

        Args:
            id: Identificador da loja
        """
        pass
