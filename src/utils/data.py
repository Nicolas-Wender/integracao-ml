from datetime import date


def get_first_and_last_day_of_last_year() -> tuple[str, str]:
    """
    Retorna o primeiro e o último dia do ano passado como strings no formato YYYY-MM-DD.
    """
    last_year = date.today().year - 1
    first_day = date(last_year, 1, 1).strftime("%Y-%m-%d")
    last_day = date(last_year, 12, 31).strftime("%Y-%m-%d")
    return first_day, last_day


from datetime import datetime, timedelta


def get_periodo_ultimos_dias(dias: int = 2):
    hoje = datetime.now()
    data_anterior = (hoje - timedelta(days=dias)).strftime("%Y-%m-%d")
    data_posterior = hoje.strftime("%Y-%m-%d")
    return data_anterior, data_posterior
