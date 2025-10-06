"""
Factory principal para criação do cliente.

Implementa o padrão Factory Method para criação do Ap
com todas as suas dependências configuradas.
"""

from typing import Optional

from src.interfaces.credentials_repository_interface import (
    ICredentialsRepository,
)
from src.interfaces.encryption_service_interface import IEncryptionService
from src.interfaces.token_manager_interface import ITokenManager

from src.repositories.credentials_repository import CredentialsRepository

from src.services.encryption_service import EncryptionService
from src.services.token_manager import TokenManager

from src.clients.client import Client

import os
from supabase import create_client, Client as SupabaseClient
from supabase.client import ClientOptions
from dotenv import load_dotenv


class Factory:
    """Factory para criação do cliente."""

    def __init__(self):
        """Inicializa a factory."""
        self._token_manager: Optional[ITokenManager] = None
        self._credentials_repository: Optional[ICredentialsRepository] = None
        self._encryption_service: Optional[IEncryptionService] = None

    def create_client(
        self,
        max_retries: int = 3,
        retry_delay: int = 1,
    ) -> Client:
        """
        Cria cliente com todas as dependências configuradas.

        Args:
            max_retries: Número máximo de tentativas para requisições
            retry_delay: Delay entre tentativas em segundos

        Returns:
            Cliente configurado
        """

        encryption_service = self.create_encryption_service()
        credentials_repository = self.create_credentials_repository(encryption_service)

        token_manager = self.create_token_manager(
            credentials_repository=credentials_repository,
        )

        return Client(
            token_manager=token_manager,
            max_retries=max_retries,
            retry_delay=retry_delay,
        )

    def create_token_manager(
        self,
        credentials_repository: Optional[ICredentialsRepository] = None,
    ) -> ITokenManager:
        """
        Cria gerenciador de tokens.

        Args:
            credentials_repository: Repositório de credenciais (opcional)

        Returns:
            Gerenciador de tokens
        """
        if self._token_manager is None:
            if not credentials_repository:
                credentials_repository = self.create_credentials_repository()
            self._token_manager = TokenManager(
                credentials_repository=credentials_repository,
            )
        return self._token_manager

    def create_credentials_repository(
        self,
        encryption_service: Optional[IEncryptionService] = None,
    ) -> ICredentialsRepository:
        """
        Cria repositório de credenciais.

        Args:
            encryption_service: Serviço de criptografia (opcional)

        Returns:
            Repositório de credenciais
        """

        load_dotenv()

        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if url is None or key is None:
            raise EnvironmentError(
                "SUPABASE_URL and SUPABASE_KEY environment variables must be set"
            )

        supabase: SupabaseClient = create_client(
            url,
            key,
            options=ClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
                schema="public",
            ),
        )

        if self._credentials_repository is None:
            if not encryption_service:
                encryption_service = self.create_encryption_service()

            self._credentials_repository = CredentialsRepository(
                encryption_service=encryption_service, supabase_client=supabase
            )
        return self._credentials_repository

    def create_encryption_service(self) -> IEncryptionService:
        """
        Cria serviço de criptografia.

        Args:
            encryption_key: Chave de criptografia (opcional)

        Returns:
            Serviço de criptografia
        """
        if self._encryption_service is None:
            self._encryption_service = EncryptionService()
        return self._encryption_service

    def reset(self) -> None:
        """Reseta todas as instâncias singleton."""
        self._token_manager = None
        self._credentials_repository = None
        self._encryption_service = None
