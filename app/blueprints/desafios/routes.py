from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models import User, Convite, Desafio
from app.ext.database import db
from . import chalenger_bp
from decimal import Decimal, ROUND_HALF_UP
import json

@chalenger_bp.route('/menu-principal')
@login_required
def menu_principal():
    desafios = current_user.desafios
    convites = Convite.query.filter_by(convidado_id=current_user.id, aceito=True).all()
    desafios_convidados = [convite.desafio for convite in convites]
    convites_pendentes = Convite.query.filter_by(convidado_id=current_user.id, aceito=False).count()
    return render_template('desafios/menu_principal.html', desafios=desafios, desafios_convidados=desafios_convidados, convites_pendentes=convites_pendentes)

@chalenger_bp.route('/novo_desafio', methods=['GET', 'POST'])
@login_required
def novo_desafio():
    if request.method == 'POST':
        nome = request.form['nome']
        meta = Decimal(request.form['meta']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        depositos_totais = int(request.form['depositos_totais'])
        valor_maximo_aporte = Decimal(request.form['valor_maximo_aporte']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        desafio = Desafio(nome=nome, meta=float(meta), depositos_totais=depositos_totais,
                          valor_maximo_aporte=float(valor_maximo_aporte), owner=current_user)
        desafio.gerar_valores_depositos()
        
        
        soma_depositos = sum(Decimal(v) for v in json.loads(desafio.valores_depositos))
        if soma_depositos != Decimal(str(desafio.meta)):
            print(f"Erro: A soma dos depósitos ({soma_depositos}) não é igual à meta ({desafio.meta})")
        else:
            print(f"Sucesso: A soma dos depósitos ({soma_depositos}) é igual à meta ({desafio.meta})")

        db.session.add(desafio)
        db.session.commit()

        flash('Novo desafio criado com sucesso!', 'success')
        return redirect(url_for('chalenger.menu_principal'))

    return render_template('desafios/novo_desafio.html')

@chalenger_bp.route('/desafio/<int:id>', methods=['GET', 'POST'])
@login_required
def desafio(id):
    desafio = Desafio.query.get_or_404(id)
    db.session.refresh(desafio)  # Força uma atualização dos dados do desafio
    
    return render_template('desafios/desafio.html', desafio=desafio)

@chalenger_bp.route('/excluir_desafio/<int:id>', methods=['POST'])
@login_required
def excluir_desafio(id):
    desafio = Desafio.query.get_or_404(id)
    if desafio.owner != current_user:
        flash('Você não tem permissão para excluir este desafio.')
        return redirect(url_for('chalenger.menu_principal'))
    
    try:
        # Primeiro, exclua todos os convites associados a este desafio
        Convite.query.filter_by(desafio_id=id).delete()
        
        # Agora, exclua o desafio
        db.session.delete(desafio)
        db.session.commit()
        flash('Desafio excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir desafio: {str(e)}', 'error')
    return redirect(url_for('chalenger.menu_principal'))

@chalenger_bp.route('/convidar/<int:desafio_id>', methods=['GET', 'POST'])
@login_required
def convidar(desafio_id):
    desafio = Desafio.query.get_or_404(desafio_id)
    if desafio.owner != current_user:
        flash('Você não tem permissão para convidar pessoas para este desafio.')
        return redirect(url_for('chalenger.menu_principal'))
    
    if request.method == 'POST':
        email = request.form['email']
        convidado = User.query.filter_by(email=email).first()
        if not convidado:
            flash('Usuário não encontrado.')
            return redirect(url_for('chalenger.convidar', desafio_id=desafio_id))
        
        convite_existente = Convite.query.filter_by(desafio_id=desafio_id, convidado_id=convidado.id).first()
        if convite_existente:
            flash('Este usuário já foi convidado para este desafio.')
            return redirect(url_for('convidar', desafio_id=desafio_id))
        
        novo_convite = Convite(desafio_id=desafio_id, convidado_id=convidado.id)
        db.session.add(novo_convite)
        db.session.commit()
        flash('Convite enviado com sucesso!')
        return redirect(url_for('chalenger.desafio', id=desafio_id))
    
    return render_template('desafios/convidar.html', desafio=desafio)

@chalenger_bp.route('/convites')
@login_required
def convites():
    convites_pendentes = Convite.query.filter_by(convidado_id=current_user.id, aceito=False).all()
    return render_template('desafios/convites.html', convites=convites_pendentes)

@chalenger_bp.route('/aceitar_convite/<int:convite_id>')
@login_required
def aceitar_convite(convite_id):
    convite = Convite.query.get_or_404(convite_id)
    if convite.convidado_id != current_user.id:
        flash('Você não tem permissão para aceitar este convite.')
        return redirect(url_for('chalenger.convites'))
    
    convite.aceito = True
    db.session.commit()
    flash('Convite aceito com sucesso!')
    return redirect(url_for('chalenger.menu_principal'))

@chalenger_bp.route('/users')
def list_users():
    users = User.query.all()
    return '<br>'.join([f'ID: {user.id}, Username: {user.username}, Email: {user.email}' for user in users])

@chalenger_bp.route('/registrar_deposito/<int:desafio_id>', methods=['POST'])
@login_required
def registrar_deposito(desafio_id):
    print(f"Recebida solicitação para registrar depósito para o desafio {desafio_id}")
    print(f"Conteúdo da requisição: {request.data}")
    
    try:
        data = request.get_json(force=True)
        print(f"Dados JSON recebidos: {data}")
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        return jsonify({'success': False, 'message': 'Dados inválidos'}), 400
    
    depositos = data.get('depositos', [])
    print(f"Depósitos a serem registrados: {depositos}")
    
    if not depositos:
        return jsonify({'success': False, 'message': 'Nenhum depósito foi selecionado.'}), 400
    
    desafio = Desafio.query.get_or_404(desafio_id)
    
    try:
        for numero in depositos:
            desafio.adicionar_deposito(int(numero))
        
        db.session.commit()
        print("Depósitos registrados com sucesso")
        return jsonify({'success': True, 'message': 'Depósitos registrados com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao registrar depósitos: {e}")
        return jsonify({'success': False, 'message': 'Erro ao registrar depósitos.'}), 500
