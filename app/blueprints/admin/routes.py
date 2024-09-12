from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import User, Desafio, Convite
from app.ext.database import db
from . import admin_bp
from app.utils import admin_required
from sqlalchemy import func


@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_desafios = Desafio.query.count()
    total_convites = Convite.query.count()
    return render_template('admin/dashboard.html', total_users=total_users, 
                           total_desafios=total_desafios, total_convites=total_convites)

# Gerenciamento de Usuários
@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.is_active = 'is_active' in request.form
        user.is_admin = 'is_admin' in request.form
        db.session.commit()
        flash('Usuário atualizado com sucesso.')
        return redirect(url_for('admin.list_users'))
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Se for uma solicitação AJAX
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify(success=True, message='Usuário excluído com sucesso.')
    else:
        # Se for uma solicitação normal
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash('Usuário excluído com sucesso.')
        return redirect(url_for('admin.list_users'))

# Gerenciamento de Desafios
@admin_bp.route('/desafios')
@login_required
@admin_required
def list_desafios():
    desafios = Desafio.query.all()
    return render_template('admin/desafios.html', desafios=desafios)

@admin_bp.route('/desafios/<int:desafio_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_desafio(desafio_id):
    desafio = Desafio.query.get_or_404(desafio_id)
    if request.method == 'POST':
        desafio.nome = request.form['nome']
        desafio.meta = float(request.form['meta'])
        desafio.data_inicio = request.form['data_inicio']
        desafio.data_fim = request.form['data_fim']
        db.session.commit()
        flash('Desafio atualizado com sucesso.')
        return redirect(url_for('admin.list_desafios'))
    return render_template('admin/edit_desafio.html', desafio=desafio)

@admin_bp.route('/desafios/<int:desafio_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_desafio(desafio_id):
    desafio = Desafio.query.get_or_404(desafio_id)
    db.session.delete(desafio)
    db.session.commit()
    flash('Desafio excluído com sucesso.')
    return redirect(url_for('admin.list_desafios'))

# Relatórios
@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    active_users = User.query.filter_by(is_active=True).count()
    total_investido = db.session.query(func.sum(Desafio.valor_investido)).scalar() or 0
    desafios_concluidos = Desafio.query.filter(Desafio.valor_investido >= Desafio.meta).count()
    
    return render_template('admin/reports.html', active_users=active_users, 
                           total_investido=total_investido, desafios_concluidos=desafios_concluidos)
