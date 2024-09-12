from flask import Flask
from flask_wtf import CSRFProtect
from flask_login import LoginManager, current_user
from app.ext.config import init_configuration
from app.blueprints.auth import auth_bp
from app.blueprints.landpage import landingpage_bp
from app.blueprints.desafios import chalenger_bp
from app.blueprints.admin import admin_bp
from app.ext.database import init_database, db
from app.ext.email import email
from app.models import User, Convite
from app.utils import format_currency
import logging
csrf = CSRFProtect()



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
    def load_user(user_id):
        user = User.query.get(int(user_id))
        if user and user.is_active:
            return user
        return None

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(chalenger_bp, url_prefix='/desafio')
    app.register_blueprint(admin_bp, url_prefix='/admin')
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

    # Configuração de logging
    logging.basicConfig(level=logging.INFO)

    return app
