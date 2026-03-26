from flask import Blueprint, render_template, request, jsonify
from .services import buscar_cotacao, buscar_historico

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    moeda = 'USD'

    if request.method == 'POST':
        moeda = request.form['moeda']
        data = request.form['data']

        resultado = buscar_cotacao(moeda, data)

    return render_template('index.html', resultado=resultado, moeda=moeda)


@main.route('/api/historico/<moeda>/<int:dias>')
def historico_api(moeda, dias):
    dados = buscar_historico(moeda, dias)
    return jsonify(dados)