from flask import Blueprint

bp = Blueprint('consultants', __name__)

from . import routes, services
