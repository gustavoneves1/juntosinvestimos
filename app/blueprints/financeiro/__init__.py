from flask import Blueprint


bolsa_bp = Blueprint('bolsa', __name__)

from . import routes  
