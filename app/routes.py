from flask import Blueprint, render_template, request
from .services import buscar_cotacao

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