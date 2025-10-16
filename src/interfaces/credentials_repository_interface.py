"""
Interface para repositório de credenciais.

Define o contrato para persistência de credenciais.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import pandas as pd


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

    @abstractmethod
    def delete_sales_by_id_and_date(
        self, id: str, start_date: str, end_date: str
    ) -> None:
        """
        Exclui registros da tabela sale_ml cujo id seja igual ao argumento e date_created esteja entre start_date e end_date.

        Args:
            id: Identificador do pedido
            start_date: Data inicial (string, formato compatível com Supabase)
            end_date: Data final (string, formato compatível com Supabase)
        """

        pass

    @abstractmethod
    def insert_sales_from_dataframe(self, df: pd.DataFrame) -> None:
        """
        Insere novos registros na tabela sales_ml a partir de um DataFrame do pandas.

        Args:
            df: DataFrame contendo os registros a serem inseridos
        """
        pass

    @abstractmethod
    def delete_ads_by_id_and_date(
        self, id: str, start_date: str, end_date: str
    ) -> None:
        """
        Exclui registros da tabela ads_ml cujo id seja igual ao argumento e date_created esteja entre start_date e end_date.

        Args:
            start_date: Data inicial (string, formato compatível com Supabase)
            end_date: Data final (string, formato compatível com Supabase)
        """
        pass

    @abstractmethod
    def insert_ads_from_dataframe(self, df: pd.DataFrame) -> None:
        """
        Insere novos registros na tabela ads_ml a partir de um DataFrame do pandas.

        Args:
            df: DataFrame contendo os registros a serem inseridos
        """
        pass

    @abstractmethod
    def get_unique_mlbs_by_id(self, id: str) -> list:
        """
        Retorna todos os MLBs únicos da tabela sales_ml de acordo com o id fornecido.

        Args:
            id: Identificador da loja

        Returns:
            Lista com os MLBs únicos
        """
        pass
