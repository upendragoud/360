from flask import Blueprint, jsonify, request
import json
import os
from flask_jwt_extended import jwt_required
from .services import *
from app.log_handler import get_logger
from app import cache
from flasgger import swag_from

logger = get_logger()

bp = Blueprint('consultants', __name__, url_prefix='/consultants')

def make_cache_key(*args, **kwargs):
    return f"consultants_{request.view_args['order_id']}"


def get_swagger_file(module_name, yaml_filename):
    module_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(module_dir, 'docs')
    return os.path.join(docs_dir, yaml_filename)


'''
    Get all consultants
'''


@bp.route('/', methods=['GET'])
@swag_from(get_swagger_file('consultants', 'consultants_all.yml'))
def get_tasks():
    consultants = get_consultant_orders_service()
    if consultants is not None:
        return consultants, 200
    else:
        return jsonify(), 200
