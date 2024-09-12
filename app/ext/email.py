from flask_mail import Mail

mail = Mail()

def email(app):
# Configurações para o seu e-mail com o domínio personalizado
    app.config['MAIL_SERVER'] = 'smtp.hostinger.com'
    app.config['MAIL_PORT'] = 465  # Porta para SSL
    app.config['MAIL_USERNAME'] = 'suporte@juntosinvestimos.com.br'
    app.config['MAIL_PASSWORD'] = '@Gnp@040794_'  # Substitua pela senha do e-mail
    app.config['MAIL_USE_TLS'] = False  # Não usa TLS com SSL
    app.config['MAIL_USE_SSL'] = True  # Usa SSL
    app.config['MAIL_DEFAULT_SENDER'] = 'suporte@juntosinvestimos.com.br'
    
    mail.init_app(app)

    return mail

