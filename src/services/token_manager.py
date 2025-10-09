"""
Gerenciador de tokens implementando ITokenManager.

Gerencia tokens OAuth com cache e refresh automático.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

import pandas as pd
import requests
import os

from src.interfaces.credentials_repository_interface import (
    ICredentialsRepository,
)
from src.interfaces.token_manager_interface import ITokenManager
from src.utils.log import log


class TokenManager(ITokenManager):
    """Gerenciador de tokens OAuth com cache e refresh automático."""

    def __init__(
        self,
        credentials_repository: ICredentialsRepository,
    ):
        """
        Inicializa o gerenciador de tokens.

        Args:
            credentials_repository: Repositório de credenciais
        """
        self._credentials_repository = credentials_repository
        self._token_cache: Dict[str, Dict[str, Any]] = {}

    def get_access_token(self, id: str, clear_cache: bool = False) -> Optional[str]:
        """
        Obtém token de acesso válido para a loja.

        Args:
            id: Identificador da loja
            clear_cache: Se True, limpa o cache antes de buscar o token

        Returns:
            Token de acesso válido ou None quando indisponível
        """

        try:
            # Verifica cache primeiro, Se não estiver no cache, busca no repositório
            if clear_cache and id in self._token_cache:
                del self._token_cache[id]

            if id in self._token_cache:
                cred = self._token_cache[id]
            else:
                cred = self._credentials_repository.get_credentials(id)

            if (
                not cred
                or not cred.get("refresh_token")
                or cred.get("refresh_token") == ""
            ):
                log.info(f"Refresh token ausente para {id}, retornando None.")
                return None

            if self.is_token_invalid(cred):
                log.info(f"Token inválido para {id}, atualizando...")
                cred = self.refresh_token(id, cred)
                self._credentials_repository.save_token(id, cred)

            self._token_cache[id] = cred

            return self._token_cache[id].get("access_token")

        except Exception as e:
            log.error(f"Erro ao obter token para {id}: {e}")
            raise

    def is_token_invalid(self, cred: Dict[str, Any]) -> bool:
        """Retorna True quando o token está expirado ou com validade inválida."""
        try:
            if (
                cred.get("access_token", "") is None
                or cred.get("access_token", "") == ""
            ):
                return True

            validade = cred.get("validade", "")
            if not validade:
                return True

            expiration = pd.to_datetime(validade, utc=True, errors="coerce")
            if pd.isna(expiration):
                return True

            current_time = datetime.now(timezone.utc)

            return current_time >= expiration.to_pydatetime()

        except Exception as exc:
            log.warning(f"Falha ao validar expiração do token: {exc}")
            return True

    def refresh_token(self, id: str, cred: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza token usando refresh_token.

        Args:
            store: Identificador da loja

        Returns:
            Novo token de acesso
        """

        try:
            if id in self._token_cache:
                del self._token_cache[id]

            headers = {
                "accept": "application/json",
                "content-type": "application/x-www-form-urlencoded",
            }
            payload = {}
            refresh_token_value = cred.get("refresh_token", "")

            if refresh_token_value or refresh_token_value != "":
                payload = {
                    "grant_type": "refresh_token",
                    "client_id": os.environ.get("ML_APP_ID"),
                    "client_secret": os.environ.get("ML_APP_SECRET"),
                    "refresh_token": refresh_token_value,
                }
            else:
                payload = self._credentials_repository.get_refresh_payload(id)

                if not payload.get("refresh_token"):
                    log.warning(
                        f"Payload de refresh sem refresh_token para {id}. Abortando atualização."
                    )
                    return {"access_token": "", "refresh_token": "", "validade": ""}

            response = requests.post(
                "https://api.mercadolibre.com/oauth/token",
                headers=headers,
                data=payload,
            )

            response = response.json()

            validade = datetime.now() + pd.Timedelta(hours=4)
            return {
                "access_token": response.get("access_token", ""),
                "refresh_token": response.get("refresh_token", ""),
                "validade": str(validade),
            }

        except Exception as e:
            log.error(f"Erro ao fazer refresh do token para {id}: {e}")
            return {"access_token": "", "refresh_token": "", "validade": ""}

    def force_refreshing_token(self, id: str) -> str:
        """
        Força a atualização do token de acesso.

        Args:
            id: Identificador da loja

        Returns:
            Novo token de acesso
        """
        try:
            cred = self._credentials_repository.get_credentials(id)

            new_cred = self.refresh_token(id, cred)

            refresh_token = new_cred.get("refresh_token", "")
            access_token = new_cred.get("access_token", "")

            if not refresh_token or not access_token:
                log.error(
                    f"Falha ao forçar refresh para {id}: tokens ausentes após tentativa."
                )
                return ""

            self._credentials_repository.save_token(id, new_cred)
            self._token_cache[id] = new_cred
            return access_token
        except Exception as e:
            log.error(f"Erro ao forçar refresh do token para {id}: {e}")
            raise

    def _obtain_new_token(self, id: str) -> None:
        """
        Obtém novo token através do fluxo OAuth.

        Args:
            store: Identificador da loja

        Returns:
            Novo token de acesso
        """

        self._credentials_repository.clear_tokens(id)
