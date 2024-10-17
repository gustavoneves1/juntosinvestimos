from flask import render_template, jsonify, request
import requests
from . import financeiro_bp
from app.utils import get_real_ibov_data, get_historico_ibov_data


@financeiro_bp.route('/')
def index():
    ibovespa_info = get_real_ibov_data()  # Dados atuais
    info_historico = get_historico_ibov_data()  # Dados históricos para o gráfico
    
    if ibovespa_info and info_historico:
        # Passando ambos os conjuntos de dados para o template
        return render_template('financeiro/resumo.html', 
                               info=ibovespa_info, 
                               historico=info_historico)
    else:
        return "Erro ao obter dados do Ibovespa", 500
    
