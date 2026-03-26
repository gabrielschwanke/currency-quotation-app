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

    except Exception as e:
        print(e)
        return "Erro ao buscar cotação"


# 🔥 NOVA FUNÇÃO PARA O GRÁFICO
def buscar_historico(moeda, dias=7):
    try:
        url = f"https://economia.awesomeapi.com.br/json/daily/{moeda}-BRL/{dias}"
        response = requests.get(url)
        dados = response.json()

        historico = []

        for item in reversed(dados):  # ordem cronológica
            historico.append({
                "data": int(item["timestamp"]),
                "valor": float(item["bid"])
            })

        return historico

    except Exception as e:
        print(e)
        return []