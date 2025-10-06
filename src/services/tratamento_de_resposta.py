import json
from typing import Any, Dict
import time
import requests

from src.utils.log import log


def tratamento_de_resposta(resp: requests.Response) -> Dict[str, Any]:
    """
    Analisa a resposta HTTP e retorna um dicionário de controle:
    {
        'retry': bool,        # Se deve tentar novamente
        'finished': bool,     # Se deve encerrar e retornar
        'response': dict      # O conteúdo da resposta
    }
    """
    try:
        resp_data = resp.json()
    except (json.JSONDecodeError, ValueError):
        resp_data = {"raw_content": resp.text}

    status = resp.status_code

    if 200 <= status < 300:
        return {"retry": False, "refresh_token": False, "response": resp_data}
    if status == 401:
        log.warning(f"Resposta 401 - Token pode estar expirado: {resp.json()}")
        return {"retry": True, "refresh_token": True, "response": resp_data}
    if status == 429:
        return {"retry": True, "refresh_token": False, "response": resp_data}
    if status == 503:
        log.warning("Resposta 503 - Serviço indisponível")
        return {"retry": False, "refresh_token": False, "response": resp_data}

    # Outros erros: não tenta novamente, retorna resposta
    return {"retry": False, "refresh_token": False, "response": resp_data}
