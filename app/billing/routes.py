from flask import Blueprint, jsonify, request
import os
from flask_jwt_extended import jwt_required
from .services import *
from app.log_handler import get_logger
from app import cache
from flasgger import swag_from

logger = get_logger()

bp = Blueprint('billing', __name__, url_prefix='/billing')

def make_cache_key(*args, **kwargs):
    return f"billing_{request.view_args['billing_id']}"


def get_swagger_file(module_name, yaml_filename):
    module_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(module_dir, 'docs')
    return os.path.join(docs_dir, yaml_filename)


'''
    Get all billing entries
'''


@bp.route('/', methods=['GET'])
@swag_from(get_swagger_file('billing', 'billing_list.yml'))
def get_billings():
    billings = get_billings_service()
    if billings is not None:
        return billings, 200
    else:
        return jsonify(), 200


'''
    Get billing details
'''


@bp.route('/<int:bid>', methods=['GET'])
@swag_from(get_swagger_file('billing', 'billing_get_by_id.yml'))
def get_billing(bid):
    billing = get_billing_service(int(bid))
    if billing is not None:
        return billing, 200
    else:
        return jsonify(), 200


'''
    Get all billing entries of a given org
'''


@bp.route('/org/<int:oid>', methods=['GET'])
@swag_from(get_swagger_file('billing', 'billing_org_get_by_id.yml'))
def get_org_billings(oid):
    billing = get_org_billings_service(int(oid))
    if billing is not None:
        return billing, 200
    else:
        return jsonify(), 200


'''
    Create billing entry(post purchase) of a template or assessor by an org
'''


@bp.route('/', methods=['POST'])
@swag_from(get_swagger_file('billing', 'billing_create.yml'))
def create_billing():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    data = request.get_json()
    billing = create_billing_service(data)
    if billing is not None:
        return billing, 200
    else:
        return jsonify(), 200

# ----------------------------------------------

@bp.route('/details/<int:user_id>', methods=['GET'])
def get_billing_route_by_user_id_routes(user_id):
    question = get_billing_by_user_id_services(user_id)
    if not question:
        return jsonify({'error': 'Billing not found'}), 404
    return jsonify(question)
