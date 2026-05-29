from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session
from .services import buscar_cotacao, buscar_historico

main = Blueprint("main", __name__)

MOEDAS_PERMITIDAS = {"USD", "EUR", "GBP", "ARS", "CAD","JPY", "CNY", "BTC", "ETH", "LTC", "DOGE"}
PERIODOS_PERMITIDOS = {7, 15, 30}


def data_valida(data_str):
    try:
        datetime.strptime(data_str, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


@main.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    moeda = "USD"
    usuario = session.get("usuario")

    if request.method == "POST":
        moeda = request.form.get("moeda", "USD").upper()
        data = request.form.get("data", "").strip()

        if moeda not in MOEDAS_PERMITIDAS:
            resultado = "Moeda inválida. Escolha USD, EUR ou BTC."
            moeda = "USD"
        elif not data_valida(data):
            resultado = "Data inválida. Selecione uma data válida."
        else:
            try:
                resultado = buscar_cotacao(moeda, data)

                if not resultado:
                    resultado = "Não foi possível obter a cotação para a data informada."
            except Exception:
                resultado = "Ocorreu um erro ao buscar a cotação. Tente novamente."

    return render_template(
        "index.html",
        resultado=resultado,
        moeda=moeda,
        usuario=usuario
    )


@main.route("/api/historico/<moeda>/<int:dias>", methods=["GET"])
def historico_api(moeda, dias):
    moeda = moeda.upper()

    if moeda not in MOEDAS_PERMITIDAS:
        return jsonify({
            "erro": "Moeda inválida. Use USD, EUR ou BTC."
        }), 400

    if dias not in PERIODOS_PERMITIDOS:
        return jsonify({
            "erro": "Período inválido. Use 7, 15 ou 30 dias."
        }), 400

    try:
        dados = buscar_historico(moeda, dias)

        if not isinstance(dados, list):
            return jsonify({
                "erro": "Formato de dados inválido retornado pelo serviço."
            }), 500

        dados_filtrados = []
        for item in dados:
            if (
                isinstance(item, dict)
                and "data" in item
                and "valor" in item
            ):
                dados_filtrados.append(item)

        dados_ordenados = sorted(dados_filtrados, key=lambda x: x["data"])

        return jsonify(dados_ordenados), 200

    except Exception:
        return jsonify({
            "erro": str(e)
        }), 500
