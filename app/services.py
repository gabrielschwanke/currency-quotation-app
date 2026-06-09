from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Tuple
import requests

BASE_URL_FIAT = "https://api.frankfurter.app"
BASE_URL_CRYPTO = "https://api.coingecko.com/api/v3"
TIMEOUT = 10
CACHE_EXPIRATION_MINUTES = 15

CRIPTOS = {"BTC", "ETH", "LTC", "DOGE"}
CRYPTO_IDS = {"BTC": "bitcoin", "ETH": "ethereum", "LTC": "litecoin", "DOGE": "dogecoin"}

_cache: Dict[str, Tuple[Any, datetime]] = {}


def _request_json(url: str) -> Any:
    agora = datetime.now()


    if url in _cache:
        dados_salvos, salvo_em = _cache[url]
        if agora - salvo_em < timedelta(minutes=CACHE_EXPIRATION_MINUTES):
            print(f"⚡ [CACHE HIT] {url}")
            return dados_salvos
 
    print(f"🌐 [API CALL] Buscando dados reais na API para: {url}")
    headers = {"User-Agent": "Mozilla/5.0"}
 
    try:
        response = requests.get(url, timeout=TIMEOUT, headers=headers)
        print("STATUS:", response.status_code)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if url in _cache:
            print("⚠️ [CACHE FALLBACK] Usando cache expirado como plano de emergência!")
            return _cache[url][0]
        raise
 
    dados = response.json()
    _cache[url] = (dados, agora)
    print("💾 [CACHE SAVED] Dados salvos em memória.")
    return dados
 
 
def _normalizar_data(data: str) -> str:
    """
    Recebe data no formato YYYY-MM-DD e devolve YYYYMMDD.
    Lança ValueError se a data for inválida.
    """
    data_obj = datetime.strptime(data, "%Y-%m-%d")
    return data_obj.strftime("%Y%m%d")
 
 
def _normalizar_timestamp(timestamp: Any) -> int:
    """
    Normaliza timestamp para segundos.
    A AwesomeAPI pode retornar segundos ou milissegundos
    dependendo do endpoint/contexto.
    """
    ts = int(timestamp)
 
    if ts > 9999999999:
        ts = ts // 1000
 
    return ts
 
 
def buscar_cotacao(moeda: str, data: str) -> str:
    try:
        moeda = moeda.upper().strip()
        datetime.strptime(data, "%Y-%m-%d")

        if moeda in CRIPTOS:
            coin_id = CRYPTO_IDS[moeda]
            url = f"{BASE_URL_CRYPTO}/coins/{coin_id}/history?date={datetime.strptime(data, '%Y-%m-%d').strftime('%d-%m-%Y')}&localization=false"
            dados = _request_json(url)
            valor = dados["market_data"]["current_price"]["brl"]
        else:
            url = f"{BASE_URL_FIAT}/{data}?from={moeda}&to=BRL"
            dados = _request_json(url)
            valor = dados["rates"]["BRL"]

        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    except ValueError:
        return "Data inválida. Use uma data válida no formato correto."
    except requests.exceptions.Timeout:
        return "A consulta demorou demais para responder. Tente novamente."
    except requests.exceptions.RequestException:
        return "Erro de conexão ao buscar a cotação."
    except (KeyError, TypeError):
        return "Cotação não encontrada para a data informada."
    except Exception:
        return "Erro ao buscar cotação."
 
 
def buscar_historico(moeda: str, dias: int = 7) -> List[Dict[str, Any]]:
    try:
        moeda = moeda.upper().strip()
        dias = int(dias)
        hoje = date.today()
        data_inicio = (hoje - timedelta(days=dias)).isoformat()
        data_fim = hoje.isoformat()

        if moeda in CRIPTOS:
            coin_id = CRYPTO_IDS[moeda]
            url = f"{BASE_URL_CRYPTO}/coins/{coin_id}/market_chart?vs_currency=brl&days={dias}&interval=daily"
            dados = _request_json(url)
            historico = [
                {"data": int(ts / 1000), "valor": round(valor, 2)}
                for ts, valor in dados.get("prices", [])
            ]
        else:
            url = f"{BASE_URL_FIAT}/{data_inicio}..{data_fim}?from={moeda}&to=BRL"
            dados = _request_json(url)
            historico = [
                {"data": int(datetime.strptime(d, "%Y-%m-%d").timestamp()), "valor": round(v, 2)}
                for d, v in dados.get("rates", {}).items()
            ]

        historico.sort(key=lambda x: x["data"])
        return historico

    except Exception:
        return []