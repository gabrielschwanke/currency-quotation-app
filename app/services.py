from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
import json
import os

BASE_URL = "https://economia.awesomeapi.com.br"
TIMEOUT = 10
CACHE_DIR = "/tmp"
CACHE_EXPIRATION_MINUTES = 15


def _request_json(url: str) -> Any:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    nome_arquivo_cache = url.replace("https://", "").replace("/", "_").replace("?", "_").replace("&", "_") + ".json"
    caminho_cache = os.path.join(CACHE_DIR, nome_arquivo_cache)

    if os.path.exists(caminho_cache):
        tempo_criacao = datetime.fromtimestamp(os.path.getmtime(caminho_cache))
        if datetime.now() - tempo_criacao < timedelta(minutes=CACHE_EXPIRATION_MINUTES):
            print(f"⚡ [CACHE HIT] Servindo dados locais para: {url}")
            with open(caminho_cache, "r", encoding="utf-8") as f:
                return json.load(f)
            
    print(f"🌐 [API CALL] Buscando dados reais na API para: {url}")   

    response = requests.get(
        url,
        timeout=TIMEOUT,
        headers=headers
    )

    print("STATUS:", response.status_code)
    if response.status_code != 200 and os.path.exists(caminho_cache):
        print("⚠️ [API ERR] Usando cache expirado como plano de emergência!")
        with open(caminho_cache, "r", encoding="utf-8") as f:
            return json.load(f)

    response.raise_for_status()
    dados_json = response.json()

    try:
        with open(caminho_cache, "w", encoding="utf-8") as f:
            json.dump(dados_json, f, ensure_ascii=False, indent=4)
        print("💾 [CACHE SAVED] Dados salvos localmente com sucesso.")
    except Exception as e:
        print(f"Erro ao salvar o arquivo de cache: {e}")

    return dados_json

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

    # Se vier em milissegundos, converte para segundos
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

        if isinstance(dados, dict) and dados.get("status"):
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

        # 🔄 Voltando para a URL original que a API aceita perfeitamente
        url = f"{BASE_URL}/json/daily/{moeda}-BRL/{dias}"
        dados = _request_json(url)

        if isinstance(dados, dict) and dados.get("status"):
            return []

        if not isinstance(dados, list) or not dados:
            return []

        historico: List[Dict[str, Any]] = []

        for item in dados:
            try:
                # 🎯 O SEGREDO: Pegamos o timestamp ou a data de criação (o que estiver disponível)
                timestamp = item.get("timestamp") or item.get("create_date")
                bid = item.get("bid")

                if timestamp is None or bid is None:
                    continue

                # Se o servidor do Render receber como texto ("2026-05-28 12:00:00")
                if isinstance(timestamp, str) and "-" in timestamp:
                    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    ts_final = int(dt.timestamp())
                else:
                    ts_final = _normalizar_timestamp(timestamp)

                historico.append(
                    {
                        "data": ts_final,
                        "valor": float(bid),
                    }
                )
            except (ValueError, TypeError):
                continue

        historico.sort(key=lambda x: x["data"])
        return historico

    except requests.exceptions.Timeout:
        return []
    except requests.exceptions.RequestException:
        return []
    except Exception:
        return []