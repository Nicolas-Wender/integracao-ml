"""
Cliente  refatorado seguindo princípios SOLID.

Esta é a nova implementação do cliente  que segue os princípios SOLID
e usa Design Patterns para uma arquitetura mais limpa e testável.
"""

import json
import time
from typing import Any, Dict, Optional

import requests

from src.services.tratamento_de_resposta import tratamento_de_resposta
from src.interfaces.token_manager_interface import ITokenManager
from src.utils.log import log


class Client:
    """
    Cliente principal da API  refatorado.

    Implementa:
    - Single Responsibility: Apenas coordena chamadas de API
    - Open/Closed: Extensível via interfaces
    - Liskov Substitution: Usa interfaces para dependencies
    - Interface Segregation: Usa interfaces específicas
    - Dependency Inversion: Depende de abstrações, não implementações
    """

    def __init__(
        self,
        token_manager: ITokenManager,
        max_retries: int,
        retry_delay: float,
    ):
        """
        Inicializa o cliente .

        Args:
            token_manager: Gerenciador de tokens
            api_client: Cliente HTTP para requisições
        """
        self._token_manager = token_manager
        self._max_retries = max_retries
        self._retry_delay = retry_delay

    def _request(
        self,
        method: str,
        url: str,
        id: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Método privado para executar requisições HTTP genéricas (GET, POST, PUT).
        """
        try:
            access_token = self._token_manager.get_access_token(id)
            if not access_token:
                log.error(f"Access token indisponível para {id}. Abortando requisição.")
                return {}

            refresh = False

            for attempt in range(self._max_retries):
                default_headers = {
                    "Accept": "application/json",
                    "Authorization": f"Bearer {access_token}",
                }

                if method in ["POST", "PUT"]:
                    default_headers["Content-Type"] = "application/json"
                if headers is not None:
                    headers = {**default_headers, **headers}
                else:
                    headers = default_headers

                if method == "GET":
                    response = requests.get(url, headers=headers)
                elif method == "POST":
                    payload = json.dumps(data) if data is not None else None
                    response = requests.post(url, headers=headers, data=payload)
                elif method == "PUT":
                    payload = json.dumps(data) if data is not None else None
                    response = requests.put(url, headers=headers, data=payload)
                else:
                    raise ValueError(f"Método HTTP não suportado: {method}")

                result = tratamento_de_resposta(response)

                if result["retry"]:
                    time.sleep(self._retry_delay)
                    if result["refresh_token"]:
                        if refresh:
                            access_token = self._token_manager.force_refreshing_token(
                                id
                            )
                        else:
                            access_token = self._token_manager.get_access_token(
                                id, clear_cache=True
                            )
                            refresh = True

                        if not access_token:
                            log.error(
                                f"Novo access token indisponível para {id} após tentativa de refresh."
                            )
                            return {}

                    continue
                return result["response"]
            return {}
        except Exception as e:
            log.error(f"Erro na requisição {method} para {id}: {e}")
            raise

    def get(
        self, url: str, id: str, headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Executa requisição GET na API .
        """
        return self._request("GET", url, id, headers=headers)

    def post(
        self,
        url: str,
        data: Dict[str, Any],
        id: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Executa requisição POST na API .
        """
        return self._request("POST", url, id, data=data, headers=headers)

    def put(
        self,
        url: str,
        data: Dict[str, Any],
        id: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Executa requisição PUT na API .
        """
        return self._request("PUT", url, id, data=data, headers=headers)
