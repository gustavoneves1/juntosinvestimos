from flask import render_template, request, redirect, url_for, flash
from flask_login import  login_user, login_required, logout_user, current_user,login_manager
from sqlalchemy import func
from app.models import User
from app.ext.database import db
from . import auth_bp


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
        login = request.form['login']  #
        password = request.form['password']
        user = User.query.filter((func.lower(User.email) == func.lower(login))).first()
        print(f"Tentativa de login para: {login}")  # Log para depuração
        if user:
            print(f"Usuário encontrado: {user.username}")  # Log para depuração
            if user.check_password(password):
                login_user(user)
                flash('Login realizado com sucesso!')
                return redirect(url_for('chalenger.menu_principal'))
            else:
                print("Senha incorreta")  # Log para depuração
        else:
            print("Usuário não encontrado")  # Log para depuração
        flash('Email/nome de usuário ou senha inválidos.')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!')
    return redirect(url_for('auth.login'))