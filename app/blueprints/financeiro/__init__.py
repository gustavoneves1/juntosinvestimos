from flask import Blueprint


financeiro_bp = Blueprint('bolsa', __name__)

from . import routes  
