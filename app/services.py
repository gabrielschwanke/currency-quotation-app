import requests

def buscar_cotacao(moeda, data):
    try:
        ano = data[0:4]
        mes = data[5:7]
        dia = data[8:10]

        url = f'https://economia.awesomeapi.com.br/json/daily/{moeda}-BRL/?start_date={ano}{mes}{dia}&end_date={ano}{mes}{dia}'
        
        response = requests.get(url)
        dados = response.json()

        if dados:
            valor = float(dados[0]['bid'])
            return f"R$ {valor:.2f}"
        else:
            return "Cotação não encontrada"

    except:
        return "Erro ao buscar cotação"