from flask import Blueprint


landingpage_bp = Blueprint('landingpage', __name__)

from . import routes  
