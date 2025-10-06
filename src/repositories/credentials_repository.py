"""
Repositório de credenciais implementando ICredentialsRepository.

Gerencia a persistência de credenciais
"""

from datetime import datetime
from typing import Any, Dict

import pandas as pd
import os
from src.interfaces.encryption_service_interface import IEncryptionService
from src.interfaces.credentials_repository_interface import (
    ICredentialsRepository,
)
from src.utils.log import log

import os
from supabase import Client


class CredentialsRepository(ICredentialsRepository):
    """Repositório de credenciais"""

    def __init__(self, encryption_service: IEncryptionService, supabase_client: Client):
        """
        Inicializa o repositório de credenciais.

        Args:
            encryption_service: Serviço de criptografia
            supabase_client: Cliente Supabase (opcional, para injeção de dependência)
        """
        self._encryption_service = encryption_service
        self._supabase = supabase_client if supabase_client is not None else supabase

    def get_credentials(self, id: str) -> Dict[str, Any]:
        """
        Requisita os dados na tabela do Supabase, utilizando o id especificado.

        Args:
            id: Identificador da loja

        Returns:
            Dict com as credenciais
        """
        cred: Dict[str, Any] = {}

        try:
            # Consulta a tabela do Supabase filtrando pelo id
            response = (
                self._supabase.table("credenciais_ml")
                .select("*")
                .eq("id", id)
                .execute()
            )

            if not hasattr(response, "data") or len(response.data) == 0:  # type: ignore
                log.error(f"Credenciais não encontradas para o id: {id}")
                raise ValueError(f"Credenciais não encontradas para o id: {id}")

            data = pd.DataFrame(response.data)  # type: ignore

            if (
                data["access_token"].isnull().all()
                or data["refresh_token"].isnull().all()
            ):
                log.error(f"Tokens inválidos para o id: {id}")
                raise ValueError(f"Tokens inválidos para o id: {id}")

            cred = data.iloc[0].to_dict()

            # Descriptografa os tokens
            cred["access_token"] = self._encryption_service.decrypt(
                cred["access_token"]
            )
            cred["refresh_token"] = self._encryption_service.decrypt(
                cred["refresh_token"]
            )

        except Exception as e:
            log.error(f"Erro ao buscar credenciais para {id}: {str(e)}")
            raise

        return cred

    def save_token(self, id: str, token: Dict[str, Any]) -> None:
        """
        Salva ou atualiza os tokens na tabela do Supabase.

        Args:
            id: Identificador da loja
            token: Dicionário contendo access_token, refresh_token e validade
        """
        table_name = "credenciais_ml"

        try:
            # Criptografa os tokens antes de salvar
            encrypted_access_token = self._encryption_service.encrypt(
                token["access_token"]
            )
            encrypted_refresh_token = self._encryption_service.encrypt(
                token["refresh_token"]
            )

            # Prepara os dados para atualização
            token_data = {
                "access_token": encrypted_access_token,
                "refresh_token": encrypted_refresh_token,
                "validade": token.get("validade", datetime.now().isoformat()),
            }

            # Verifica se o registro já existe
            check = self._supabase.table(table_name).select("id").eq("id", id).execute()

            if not hasattr(check, "data") or len(check.data) == 0:  # type: ignore
                log.error(f"Credenciais não encontradas para o id: {id}")
                raise ValueError(f"Credenciais não encontradas para o id: {id}")

            check_data = check.data  # type: ignore

            if check_data and len(check_data) > 0:
                self._supabase.table(table_name).update(token_data).eq(
                    "id", id
                ).execute()

                log.info(f"Tokens atualizados para a loja {id}")
            else:
                raise ValueError(f"Falha ao salvar tokens para o id: {id}")

        except Exception as e:
            log.error(f"Erro ao salvar tokens para {id}: {str(e)}")
            raise

    def get_refresh_payload(self, id: str) -> Dict[str, Any]:
        """
        Retorna o payload para refresh_token, buscando client_id e client_secret do Supabase conforme o id.

        Args:
            id: Identificador da loja

        Returns:
            Dicionário com grant_type, client_id, client_secret, refresh_token
        """
        try:
            response = (
                self._supabase.table("credenciais_ml")
                .select("client_id,client_secret,refresh_token")
                .eq("id", id)
                .execute()
            )

            if not hasattr(response, "data") or len(response.data) == 0:  # type: ignore
                log.error(
                    f"Erro ao obter dados para payload de refresh_token para {id}"
                )
                raise ValueError(
                    f"Erro ao obter dados para payload de refresh_token para {id}"
                )

            cred: dict = response.data[0]  # type: ignore

            return {
                "grant_type": "refresh_token",
                "client_id": cred.get("client_id", ""),
                "client_secret": self._encryption_service.decrypt(
                    cred.get("client_secret", "")
                ),
                "refresh_token": cred.get("refresh_token", ""),
            }

        except Exception as e:
            log.error(f"Erro ao montar payload de refresh_token para {id}: {str(e)}")
            raise

    def clear_tokens(self, id: str) -> None:
        """
        Limpa os valores de access_token e refresh_token da tabela credenciais_ml para o id informado.

        Args:
            id: Identificador da loja
        """
        try:
            response = (
                self._supabase.table("credenciais_ml")
                .update({"access_token": "", "refresh_token": ""})
                .eq("id", id)
                .execute()
            )

            if hasattr(response, "data") and response.data:  # type: ignore
                log.info(f"Tokens limpos para a loja {id}")
            else:
                log.warning(
                    f"Nenhum registro atualizado ao limpar tokens para o id: {id}"
                )

        except Exception as e:
            log.error(f"Erro ao limpar tokens para {id}: {str(e)}")
            raise

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
        try:
            response = (
                self._supabase.table("sales_ml")
                .delete()
                .eq("id", id)
                .gte("date_created", start_date)
                .lte("date_created", end_date)
                .execute()
            )
            if hasattr(response, "data") and response.data:  # type: ignore
                log.info(
                    f"Registros excluídos para id={id} entre {start_date} e {end_date}"
                )
            else:
                log.warning(
                    f"Nenhum registro excluído para id={id} entre {start_date} e {end_date}"
                )
        except Exception as e:
            log.error(f"Erro ao excluir registros para id={id}: {str(e)}")
            raise

    def insert_sales_from_dataframe(self, df: pd.DataFrame) -> None:
        """
        Insere novos registros na tabela sales_ml a partir de um DataFrame do pandas.

        Args:
            df: DataFrame contendo os registros a serem inseridos
        """
        try:
            records = [
                {str(k): v for k, v in record.items()}
                for record in df.to_dict(orient="records")
            ]
            response = self._supabase.table("sales_ml").insert(records).execute()

            if hasattr(response, "data") and response.data:  # type: ignore
                log.info(f"{len(response.data)} registros inseridos na tabela sales_ml") # type: ignore
            else:
                log.warning("Nenhum registro foi inserido na tabela sales_ml")

        except Exception as e:
            log.error(f"Erro ao inserir registros na tabela sales_ml: {str(e)}")
            raise
