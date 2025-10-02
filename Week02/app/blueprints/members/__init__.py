from flask import Blueprint

members_bp = Blueprint('members', __name__, template_folder='../../templates')

from . import routes