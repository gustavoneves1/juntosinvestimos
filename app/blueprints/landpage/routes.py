from . import landingpage_bp
from flask import render_template, request, jsonify
from flask_login import current_user
from app.models import Feedback
from app.ext.database import db

@landingpage_bp.route('/')
def index():
    return render_template('index.html')


@landingpage_bp.route('/contribua')
def contribua():
    return render_template('contribua.html')



@landingpage_bp.route('/feedback', methods=['POST'])
def feedback():
    if request.method == 'POST':
        data = request.json
        message = data.get('message')
        feedback_type = data.get('type')
        user_id = current_user.id  # Adicione este campo ao JSON enviado do cliente

        if message and feedback_type and user_id is not None:
            new_feedback = Feedback(message=message, type=feedback_type, user_id=user_id)
            db.session.add(new_feedback)
            db.session.commit()
            return jsonify({"response": "Feedback recebido com sucesso!"}), 200
        else:
            return jsonify({"error": "Dados incompletos!"}), 400