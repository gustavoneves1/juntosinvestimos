import requests

# Seu token de autenticação
token = "rHGCchsbc3VfwWCebonK7B"

# URL da API da Brapi para o IBOVESPA com token como query param
url = f"https://brapi.dev/api/quote/PETR4?token={token}"

# Faz a requisição GET para a API
try:
    response = requests.get(url, timeout=10)  # Adiciona um timeout de 10 segundos
    
    # Verifica se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Converte a resposta JSON em um dicionário Python
        data = response.json()
        print(data)

        # Verifica se há resultados
        if 'results' in data and len(data['results']) > 0:
            # Extrai os dados do IBOVESPA
            ibov_data = data['results'][0]

            # Exibe informações básicas
            print(f"Nome: {ibov_data['longName']}")
            print(f"Símbolo: {ibov_data['symbol']}")
            print(f"Último preço: {ibov_data['regularMarketPrice']}")
            print(f"Variação do dia: {ibov_data['regularMarketChangePercent']}%")
            print(f"Máxima do dia: {ibov_data['regularMarketDayHigh']}")
            print(f"Mínima do dia: {ibov_data['regularMarketDayLow']}")
            print(f"Volume: {ibov_data['regularMarketVolume']}")
        else:
            print("Nenhum dado encontrado para o IBOVESPA.")
    else:
        print(f"Erro na requisição: {response.status_code} - {response.reason}")

except requests.exceptions.RequestException as e:
    print(f"Erro ao fazer a requisição: {e}")
