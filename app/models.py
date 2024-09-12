from app.ext.database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import random 
from decimal import Decimal, ROUND_HALF_UP
import json
from datetime import datetime, timedelta
import os
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(456)) 
    telefone_numero = db.Column(db.String(25), nullable=True)
    desafios = db.relationship('Desafio', backref='owner', lazy='dynamic')
    reset_token = db.Column(db.String(456))
    token_expiration = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_confirmed = db.Column(db.Boolean, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def generate_confirmation_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt='email-confirm')

    @staticmethod
    def verify_confirmation_token(token, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, salt='email-confirm', max_age=expiration)
        except:
            return None
        return User.query.get(data['user_id'])

    def confirm_email(self):
        self.is_confirmed = True
        self.confirmed_on = datetime.utcnow()
        db.session.add(self)

    def generate_activation_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_activation_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=3600)['user_id']
        except:
            return None
        return User.query.get(user_id)

class Desafio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    meta = db.Column(db.Float, nullable=False)
    depositos_totais = db.Column(db.Integer, nullable=False)
    depositos_feitos = db.Column(db.String, default='[]')
    valor_investido = db.Column(db.Float, default=0)
    valores_depositos = db.Column(db.String, default='[]')
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    valor_maximo_aporte = db.Column(db.Float, nullable=False)

    def gerar_valores_depositos(self):
        valores = []
        valor_restante = Decimal(str(self.meta)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        depositos_restantes = self.depositos_totais
        valor_maximo_aporte = Decimal(str(self.valor_maximo_aporte)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        while depositos_restantes > 1:
            valor_minimo = max(Decimal('1.00'), valor_restante - (depositos_restantes - 1) * valor_maximo_aporte)
            valor_maximo = min(valor_maximo_aporte, valor_restante - Decimal(str(depositos_restantes - 1)))

            valor = Decimal(str(random.uniform(float(valor_minimo), float(valor_maximo)))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            valores.append(valor)
            valor_restante -= valor
            depositos_restantes -= 1

        valores.append(valor_restante)
        valores.sort(reverse=False)

        self.valores_depositos = json.dumps([str(v) for v in valores])

        soma_ajustada = sum(Decimal(v) for v in json.loads(self.valores_depositos))
        if soma_ajustada != Decimal(str(self.meta)):
            print(f"Erro: A soma dos depósitos ({soma_ajustada}) não é igual à meta ({self.meta})")

    def get_valores_depositos(self):
        return [Decimal(v) for v in json.loads(self.valores_depositos)]

    def get_depositos_feitos(self):
        return json.loads(self.depositos_feitos)

    def set_depositos_feitos(self, depositos):
        self.depositos_feitos = json.dumps(depositos)

    def atualizar_valor_investido(self):
        valores_depositos = self.get_valores_depositos()
        depositos_feitos = self.get_depositos_feitos()
        
        valor_investido = sum(valores_depositos[i-1] for i in depositos_feitos)
        self.valor_investido = float(Decimal(str(valor_investido)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    def adicionar_deposito(self, numero):
        depositos = json.loads(self.depositos_feitos)
        if numero not in depositos:
            depositos.append(numero)
            self.depositos_feitos = json.dumps(depositos)
            self.atualizar_valor_investido()
        print(f"Depósito {numero} adicionado. Depósitos feitos: {self.depositos_feitos}")

    def get_depositos_feitos(self):
        return json.loads(self.depositos_feitos)

class Convite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    desafio_id = db.Column(db.Integer, db.ForeignKey('desafio.id', ondelete='CASCADE'), nullable=False)
    convidado_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    aceito = db.Column(db.Boolean, default=False)
    desafio = db.relationship('Desafio', backref='convites')
    convidado = db.relationship('User', backref='convites_recebidos')



class Feedback(db.Model):

    __tablename__ = 'userfeedback'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    message = db.Column(db.String(1500))
    type = db.Column(db.String(50))
    user_id = db.Column(db.Integer)