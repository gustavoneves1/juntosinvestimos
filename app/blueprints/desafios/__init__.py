from flask import Blueprint


chalenger_bp = Blueprint('chalenger', __name__)

from . import routes  
