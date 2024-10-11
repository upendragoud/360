from flask import Blueprint

bp = Blueprint('coe_team', __name__)

from . import routes, services
