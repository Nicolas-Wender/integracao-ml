import sys
import time
from typing import Any, Dict, List

import pandas as pd

from datetime import datetime
from src import api
from src.utils.data import get_periodo_ultimos_dias, get_first_and_last_day_of_last_year
from src.utils.log import log
from src.factories.factory import Factory


def get_vendas_ml(
    id: str,
    data_inicial: str,
    data_final: str,
    data_inicial_ano: str,
    data_final_ano: str,
) -> bool:
    repository = Factory().create_credentials_repository()
    erros = []

    dados_vendas: List[Dict[str, Any]] = []

    offset = 0

    data_inicial_padrao = data_inicial + "T00:00:00Z"

    while True:
        try:
            response = api.get(
                f"https://api.mercadolibre.com/orders/search?offset={offset}&limit=50&seller={id}&order.status=paid&order.date_created.from={data_inicial_padrao}&order.date_created.to={data_final}T23:59:59Z&sort=date_asc",
                id,
            )

            if response == {} or response == None:
                if len(erros) > 30:
                    break
                erros.append(f"Resposta vazia ou nula para {id}")
                continue

            for pedido in response.get("results", []):
                for order in pedido.get("order_items", []):
                    # Formata a data para yyyy-mm-dd
                    date_created_raw = pedido.get("date_created", "")
                    try:
                        date_created_fmt = (
                            datetime.strptime(
                                date_created_raw[:10], "%Y-%m-%d"
                            ).strftime("%Y-%m-%d")
                            if date_created_raw
                            else ""
                        )
                    except Exception:
                        date_created_fmt = ""

                    dados_vendas.append(
                        {
                            "Número_do_pedido_multiloja": pedido.get("id", 0),
                            "pack_id": pedido.get("pack_id", 0),
                            "title": order.get("item", {}).get("title", ""),
                            "category_id": order.get("item", {}).get("category_id", ""),
                            "mlb": order.get("item", {}).get("id", ""),
                            "seller_sku": order.get("item", {}).get("seller_sku", ""),
                            "quantity": order.get("quantity", 0),
                            "unit_price": order.get("unit_price", 0.0),
                            "full_unit_price": order.get("full_unit_price", 0.0),
                            "sale_fee": order.get("sale_fee", 0.0),
                            "listing_type_id": order.get("listing_type_id", ""),
                            "pack_id": pedido.get("pack_id", 0),
                            "date_created": date_created_fmt,
                            "paid_amount": pedido.get("paid_amount", 0.0),
                            "id": id,
                        }
                    )

            if offset >= response.get("paging", {}).get("total", 0):
                break

            offset += 50

            if offset >= 10000:
                data_inicial_padrao = pedido.get("date_created", "")
                offset = 0

        except Exception as e:
            log.error(f"Vendas ML: Error get_vendas_ml: {e}")
            break

    if len(dados_vendas) > 0:
        df_vendas_ml = pd.DataFrame(dados_vendas)
        df_vendas_ml = df_vendas_ml.fillna(
            {
                "Número_do_pedido_multiloja": 0,
                "title": "",
                "category_id": "",
                "mlb": "",
                "seller_sku": "",
                "quantity": 0,
                "unit_price": 0.0,
                "full_unit_price": 0.0,
                "sale_fee": 0.0,
                "listing_type_id": "",
                "pack_id": 0,
                "date_created": "",
                "paid_amount": 0.0,
                "id": id,
            }
        )

        repository.delete_sales_by_id_and_date(id, data_inicial_ano, data_final_ano)
        repository.delete_sales_by_id_and_date(id, data_inicial, data_final)

        repository.insert_sales_from_dataframe(df_vendas_ml)

    return True


if __name__ == "__main__":
    start_time = time.time()

    # id = sys.argv[1]
    # periodo = sys.argv[2]
    # data_inicial_ano, data_final_ano = get_first_and_last_day_of_last_year()

    # if periodo == "short":
    #     data_anterior, data_posterior = get_periodo_ultimos_dias(7)
    # else:
    #     data_anterior, data_posterior = get_periodo_ultimos_dias(120)

    # get_vendas_ml(id, data_anterior, data_posterior, data_inicial_ano, data_final_ano)

    end_time = time.time()
    print(f"Vendas ML requisitadas em {end_time - start_time:.2f} segundos")
