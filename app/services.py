from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple
import requests

BASE_URL = "https://economia.awesomeapi.com.br"
TIMEOUT = 10
CACHE_EXPIRATION_MINUTES = 15

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
    """
    Busca a cotação de uma moeda para uma data específica.
    Retorna string formatada para exibição no template.
    """
    try:
        moeda = moeda.upper().strip()
        data_formatada = _normalizar_data(data)
 
        url = (
            f"{BASE_URL}/json/daily/{moeda}-BRL/"
            f"?start_date={data_formatada}&end_date={data_formatada}"
        )
 
        dados = _request_json(url)
 
        if isinstance(dados, dict) and dados.get("status") == 404:
            return "Cotação não encontrada para a moeda informada."
 
        if not isinstance(dados, list) or not dados:
            return "Cotação não encontrada para a data informada."
 
        item = dados[0]
        bid = item.get("bid")
 
        if bid is None:
            return "Cotação indisponível no momento."
 
        valor = float(bid)
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
 
    except ValueError:
        return "Data inválida. Use uma data válida no formato correto."
    except requests.exceptions.Timeout:
        return "A consulta demorou demais para responder. Tente novamente."
    except requests.exceptions.RequestException:
        return "Erro de conexão ao buscar a cotação."
    except (KeyError, TypeError, IndexError):
        return "Resposta inválida ao buscar a cotação."
    except Exception:
        return "Erro ao buscar cotação."
 
 
def buscar_historico(moeda: str, dias: int = 7) -> List[Dict[str, Any]]:
    """
    Busca histórico de fechamento da moeda nos últimos dias.
    Retorna lista no formato:
    [
        {"data": 1711843200, "valor": 5.12},
        ...
    ]
    """
    try:
        moeda = moeda.upper().strip()
        dias = int(dias)
 
        url = f"{BASE_URL}/json/daily/{moeda}-BRL/{dias}"
        dados = _request_json(url)
 
        if isinstance(dados, dict) and dados.get("status") == 404:
            return []
 
        if not isinstance(dados, list) or not dados:
            return []
 
        historico: List[Dict[str, Any]] = []
 
        for item in dados:
            try:
                timestamp = item.get("timestamp") or item.get("create_date")
                bid = item.get("bid")
 
                if timestamp is None or bid is None:
                    continue
 
                if isinstance(timestamp, str) and "-" in timestamp:
                    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    ts_final = int(dt.timestamp())
                else:
                    ts_final = _normalizar_timestamp(timestamp)
 
                historico.append({
                    "data": ts_final,
                    "valor": float(bid),
                })
            except (ValueError, TypeError):
                continue
 
        historico.sort(key=lambda x: x["data"])
        return historico
 
    except Exception:
        return []