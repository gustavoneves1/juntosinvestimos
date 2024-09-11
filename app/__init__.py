from flask import Flask
from flask_wtf import CSRFProtect
from flask_login import LoginManager, current_user
from app.ext.config import init_configuration
from app.blueprints.auth import auth_bp
from app.blueprints.landpage import landingpage_bp
from app.blueprints.desafios import chalenger_bp
from app.ext.database import init_database, db
from app.ext.email import email
from app.models import User, Convite

csrf = CSRFProtect()

def format_currency(value,  decimal_places=2, grouping=True):
    """
    Formata um valor como moeda com ou sem agrupamento de milhares.
    
    :param value: O valor numérico a ser formatado.
    :param currency_symbol: O símbolo da moeda a ser usado.
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
        grouped_integer = ','.join([integer_part[i:i+3] for i in range(0, len(integer_part), 3)])[::-1]
        
        return f"{grouped_integer}.{decimal_part}"
    else:
        # Sem agrupamento de milhares
        return f"{value:.{decimal_places}f}"

def create_app():
    app = Flask(__name__)
    
    csrf.init_app(app)
    
    # Desabilitar CSRF temporariamente para depuração
    app.config['WTF_CSRF_ENABLED'] = True
    
    init_configuration(app)
    email(app)
    
    init_database(app)
    
    login_manager = LoginManager(app)

    @login_manager.user_loader
    def get_user(user_id):
        print(f"Buscando usuário com ID: {user_id}")
        user = User.query.filter_by(id=user_id).first()
        if user:
            print(f"Usuário encontrado: {user.email}")
        else:
            print("Usuário não encontrado")
        return user

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(chalenger_bp, url_prefix='/desafio')
    app.register_blueprint(landingpage_bp, url_prefix='/')
    
    @app.context_processor
    def inject_convites_pendentes():
        if current_user.is_authenticated:
            convites_pendentes = Convite.query.filter_by(convidado_id=current_user.id, aceito=False).count()
            return dict(convites_pendentes=convites_pendentes)
        return dict(convites_pendentes=0)
    
    @app.template_filter('format_currency')
    def format_currency_filter(value):
        return format_currency(value)

    return app
