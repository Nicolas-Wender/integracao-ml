"""
Interface para gerenciamento de tokens OAuth.

Define o contrato para serviços que gerenciam tokens de acesso.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd


class ITokenManager(ABC):
    """Interface para gerenciamento de tokens OAuth."""

    @abstractmethod
    def get_access_token(self, id: str, clear_cache: bool = False) -> str:
        """
        Obtém token de acesso válido para a loja.

        Args:
            id: Identificador da loja
            clear_cache: Se True, limpa o cache antes de buscar o token

        Returns:
            Token de acesso válido
        """
        pass

    @abstractmethod
    def is_token_invalid(self, validade: str) -> bool:
        """
        Verifica se o token atual é válido.

        Args:
            validade: Data de validade do token
        Returns:
            True se o token é inválido, False caso contrário
        """
        pass

    @abstractmethod
    def refresh_token(self, id: str, cred: pd.Series) -> Dict[str, Any]:
        """
        Atualiza o token de acesso usando o refresh token.

        Args:
            id: Identificador da loja
            cred: Série de credenciais
        Returns:
            Novo token de acesso
        Raises:
            Exception: Se falhar ao atualizar o token
        """
        pass

    @abstractmethod
    def force_refreshing_token(self, id: str) -> str:
        """
        Força a atualização do token de acesso.

        Args:
            id: Identificador da loja

        Returns:
            Novo token de acesso
        """
        pass
