from flask import url_for, current_app, abort
from flask_login import current_user
from flask_mail import Message
from app.ext.email import mail
import logging
from functools import wraps
import requests
import datetime


def format_currency(value, decimal_places=2, grouping=True):
    """
    Formata um valor como moeda com ou sem agrupamento de milhares no padrão brasileiro.
    
    :param value: O valor numérico a ser formatado.
    :param decimal_places: O número de casas decimais a ser exibido.
    :param grouping: Se True, usa agrupamento de milhares.
    :return: O valor formatado como string.
    """
    if grouping:
        # Formatação com agrupamento de milhares
        parts = f"{value:.{decimal_places}f}".split(".")
        integer_part = parts[0]
        decimal_part = parts[1]
        
        # Agrupamento de milhares
        integer_part = integer_part[::-1]
        grouped_integer = '.'.join([integer_part[i:i+3] for i in range(0, len(integer_part), 3)])[::-1]
        
        return f"R${grouped_integer},{decimal_part}"
    else:
        # Sem agrupamento de milhares
        return f"R${value:.{decimal_places}f}"

def send_reset_email(user):
    token = user.generate_reset_token()
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    subject = 'Solicitação de Redefinição de Senha'
    sender = current_app.config['MAIL_DEFAULT_SENDER']
    recipients = [user.email]
    
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = f"""
    Para redefinir sua senha, visite o seguinte link:
    {reset_url}

    Se você não fez esta solicitação, simplesmente ignore este email.
    """
    
    try:
        mail.send(msg)
        logging.info(f"Email de redefinição de senha enviado para {user.email}")
        return True
    except Exception as e:
        logging.error(f"Erro ao enviar email para {user.email}: {str(e)}")
        return False

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)



TOKEN = "rHGCchsbc3VfwWCebonK7B"

def get_real_ibov_data():
    url = "https://brapi.dev/api/quote/^BVSP"
    params = {
        'range': '1d',
        'interval': '1m',
        'fundamental': 'true',
        'dividends': 'true',
        'modules': 'balanceSheetHistory',
        'token': TOKEN,
    }

    response = requests.get(url, params=params)

   

    if response.status_code == 200:
        data = response.json()
        if "results" in data and data["results"]:
            ibovespa_data = data["results"][0]
            fechamento_anterior = ibovespa_data["regularMarketPreviousClose"]
            variacao = ibovespa_data["regularMarketChange"]
            variacao_percentual = ibovespa_data["regularMarketChangePercent"]
            fechamento = ibovespa_data["regularMarketPrice"]
            
            fechamento_anterior = f"{fechamento_anterior:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            variacao = f"{variacao:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            variacao_percentual = f"{variacao_percentual:.2f}"
            fechamento = f"{fechamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            return {
                "fechamento_anterior": fechamento_anterior,
                "variacao": variacao,
                "variacao_percentual": variacao_percentual,
                "fechamento": fechamento
            }
    return None  
def get_historico_ibov_data():
    url = "https://brapi.dev/api/quote/^BVSP"
    params = {
        'range': '1y',
        'interval': '1d',
        'fundamental': 'true',
        'dividends': 'true',
        'token': TOKEN,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        if "results" in data and data["results"]:
            ibovespa_data = data["results"][0]
            if "historicalDataPrice" in ibovespa_data:
                historico = ibovespa_data["historicalDataPrice"]

                datas = []
                precos_fechamento = []

                for registro in historico:
                    # Converte o timestamp para uma data legível
                    data_formatada = datetime.datetime.utcfromtimestamp(registro["date"]).strftime('%Y-%m-%d')
                    fechamento = registro["close"]
                    datas.append(data_formatada)
                    precos_fechamento.append(fechamento)
                    

                return {"datas": datas, "fechamento": precos_fechamento}
    
    return None  # Se não receber 200 ou não houver "results", retorne None
