from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import psycopg2
from urllib.parse import quote_plus



db = SQLAlchemy()
migrate = Migrate()

def init_database(app):
    password = quote_plus("@Gnp@040794_")
#    Construir a URI de conexão com a senha codificada
    connection_uri = f"postgresql://postgres.tnhjnemsurdckpipskks:{password}@aws-0-us-west-1.pooler.supabase.com:6543/postgres?client_encoding=utf8"
    app.config['SQLALCHEMY_DATABASE_URI'] = connection_uri

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    migrate.init_app(app, db)


