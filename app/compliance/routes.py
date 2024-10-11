from flask import Blueprint, jsonify, request
import json
from flask_jwt_extended import jwt_required
from .services import *
from app.log_handler import get_logger

logger = get_logger()

bp = Blueprint('compliance', __name__, url_prefix='/compliance')




@bp.route('/fetch/<int:org_id>/<int:resource_owner_id>', methods=['GET'])
def get_compliance_details_for_resource_route(org_id, resource_owner_id):
    compliance = get_compliance_details_for_resource_service(org_id, resource_owner_id)
    if compliance is not None:
        return compliance, 200
    else:
        return jsonify(), 400
    


@bp.route('/fetch/<int:org_id>/<int:resource_owner_id>', methods=['GET'])
def get_compliance_details_for_compliance_route(org_id, resource_owner_id):
    compliance = get_compliance_details_for_compliance_service(org_id, resource_owner_id)
    if compliance is not None:
        return compliance, 200
    else:
        return jsonify(), 400




@bp.route('/fetch/<int:org_id>/<int:resource_owner_id>/<selected_compliance>/report', methods=['GET'])
def get_compliance_details_reports_route(org_id, resource_owner_id, selected_compliance):
    pdf_response = get_compliance_details_reports_service(org_id, resource_owner_id, selected_compliance)
    
    if pdf_response is not None:
        return pdf_response
    else:
        return jsonify({"error": "Could not fetch compliance details."}), 400




@bp.route('/check_security', methods=['POST'])
def check_security():
    data = request.json
    repo_owner = data.get('repo_owner')
    repo_name = data.get('repo_name')
    github_token = data.get('github_token')

    if not all([repo_owner, repo_name, github_token]):
        return jsonify({'error': 'Missing one or more required parameters: repo_owner, repo_name, github_token'}), 400

    # bandit_result = run_bandit()
    gitleaks_result = run_gitleaks()
    github_alerts = check_github_security_alerts(repo_owner, repo_name, github_token)

    result = {
        # 'bandit_result': bandit_result,
        'gitleaks_result': gitleaks_result,
        'github_alerts': github_alerts
    }

    return jsonify({'message': result}), 200














from fastapi import FastAPI
from pydantic import BaseModel
from .services import scan_repo

app = FastAPI()

class RepoData(BaseModel):
    repo_url: str

@app.post("/scan")
async def scan_repository(repo: RepoData):
    """
    Accepts a repository URL and returns the scan results.
    """
    result = scan_repo(repo.repo_url)
    return {"scan_results": result}

