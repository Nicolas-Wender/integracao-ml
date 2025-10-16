import time
import pandas as pd
from tqdm import tqdm
from src import api
from src.utils.data import get_periodo_ultimos_dias, get_first_and_last_day_of_last_year
from src.factories.factory import Factory


def req_ads(
    id: str,
    data_inicial: str,
    data_final: str,
    data_inicial_ano: str,
    data_final_ano: str,
) -> bool:
    repository = Factory().create_credentials_repository()
    dados_ads = pd.DataFrame({})
    lista_mlb = repository.get_unique_mlbs_by_id(id)

    for mlb in tqdm(lista_mlb):
        result = api.get(
            f"https://api.mercadolibre.com/advertising/MLB/product_ads/ads/{mlb}?limit=1&offset=0&date_from={data_anterior}&date_to={data_posterior}&metrics=clicks,prints,ctr,cost,cpc,acos,organic_units_quantity,organic_units_amount,organic_items_quantity,direct_items_quantity,indirect_items_quantity,advertising_items_quantity,cvr,roas,sov,direct_units_quantity,indirect_units_quantity,units_quantity,direct_amount,indirect_amount,total_amount&aggregation_type=DAILY",
            id,
            {"api-version": "2"},
        )

        df_result = pd.DataFrame(result["results"])
        df_result["mlb"] = mlb
        df_result["id"] = id

        if result and "date" in df_result.columns:
            df_result["date"] = pd.to_datetime(df_result["date"])
            df_result = df_result.sort_values("date").reset_index(drop=True)

        dados_ads = pd.concat([dados_ads, df_result], ignore_index=True)

    if len(dados_ads) > 0:
        df_vendas_ml = pd.DataFrame(dados_ads)
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

        repository.delete_ads_by_id_and_date(id, data_inicial_ano, data_final_ano)
        repository.delete_ads_by_id_and_date(id, data_inicial, data_final)

        repository.insert_ads_from_dataframe(df_vendas_ml)

    return True


if __name__ == "__main__":
    start_time = time.time()

    # id = sys.argv[1]
    # periodo = sys.argv[2]

    id = "179385579"
    periodo = "short"

    data_inicial_ano, data_final_ano = get_first_and_last_day_of_last_year()

    if periodo == "short":
        data_anterior, data_posterior = get_periodo_ultimos_dias(7)
    else:
        data_anterior, data_posterior = get_periodo_ultimos_dias(120)

    req_ads(id, data_anterior, data_posterior, data_inicial_ano, data_final_ano)

    end_time = time.time()
    print(f"Vendas ML requisitadas em {end_time - start_time:.2f} segundos")
