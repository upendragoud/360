from flask import Blueprint

bp = Blueprint('dashboard', __name__)

from . import routes, services
