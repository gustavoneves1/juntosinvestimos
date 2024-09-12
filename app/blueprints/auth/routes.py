from flask import render_template, request, redirect, url_for, flash
from flask_login import  login_user, login_required, logout_user, current_user
from sqlalchemy import func
from app.models import User
from app.ext.database import db
from . import auth_bp
import datetime
from app.utils import send_reset_email
from werkzeug.security import generate_password_hash
import logging

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone_number = request.form['telefone']

        user = User.query.filter((User.email == email)).first()
        if user:
            flash('Nome de usuário ou email já existe.')
            return redirect(url_for('auth.register'))
        
        new_user = User(username=username, email=email, telefone_numero=phone_number)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        print(f"Novo usuário registrado: {username}, {email}")  
        flash('Registro realizado com sucesso!')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = User.query.filter((func.lower(User.email) == func.lower(login))).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login realizado com sucesso!')
            return redirect(url_for('chalenger.menu_principal'))
        flash('Email/nome de usuário ou senha inválidos.')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!')
    return redirect(url_for('auth.login'))


@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('landingpage.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            if send_reset_email(user):
                flash('Um email com instruções para redefinir sua senha foi enviado.', 'success')
                logging.info(f"Email de redefinição de senha solicitado para {email}")
            else:
                flash('Ocorreu um erro ao enviar o email. Por favor, tente novamente mais tarde.', 'error')
                logging.error(f"Falha ao enviar email de redefinição de senha para {email}")
        else:
            flash('Não foi encontrada uma conta com esse endereço de email.', 'warning')
            logging.warning(f"Tentativa de redefinição de senha para email não cadastrado: {email}")
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('landingpage.index'))
    
    user = User.verify_reset_token(token)
    if user is None:
        flash('O token é inválido ou expirou', 'warning')
        return redirect(url_for('auth.reset_password_request'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('As senhas devem ser iguais', 'warning')
            return redirect(url_for('auth.reset_password', token=token))
        
        try:
            user.set_password(password)
            db.session.commit()
            flash('Sua senha foi atualizada com sucesso', 'success')
            logging.info(f"Senha redefinida com sucesso para o usuário: {user.email}")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Ocorreu um erro ao atualizar a senha. Por favor, tente novamente.', 'error')
            logging.error(f"Erro ao redefinir senha para o usuário {user.email}: {str(e)}")
            return redirect(url_for('auth.reset_password', token=token))
    
    return render_template('auth/reset_password.html')