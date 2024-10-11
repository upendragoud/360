from app import db
import json
import time
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from .models import Compliance
from app.log_handler import get_logger
from sqlalchemy import and_
from app.resources.models import Resources


from flask import  make_response
from fpdf import FPDF
from textwrap import wrap
from datetime import datetime


import os
import subprocess
import requests

logger = get_logger()

def get_compliance_details_for_resource_service(org_id, resource_owner_id):
    try:
        resource_id = db.session.query(Resources.resource_id).filter(Resources.resource_owner == resource_owner_id).first()
        query = db.session.query(Compliance).filter(Compliance.org_id == org_id, Compliance.resource_id == resource_id[0]).all()
        list_ = []
        for q in query:
            list_.append(Compliance.to_dict(q))
        return jsonify(list_)
    except Exception as e:
        logger.error(f"Error fetching consultants: {e}")
        return None




def get_compliance_details_for_compliance_service(org_id, resource_owner_id):
    try:
        resource_id = db.session.query(Resources.resource_id).filter(Resources.resource_owner == resource_owner_id).first()
        query = db.session.query(Compliance).filter(Compliance.org_id == org_id, Compliance.resource_id == resource_id[0]).all()
        list_ = []
        for q in query:
            list_.append(Compliance.to_dict(q))
        return jsonify(list_)
    except Exception as e:
        logger.error(f"Error fetching consultants: {e}")
        return None



def get_downloads_folder():
    if os.name == 'nt':  
        return os.path.join(os.environ['USERPROFILE'], 'Downloads')
    else:  
        return os.path.join(os.path.expanduser('~'), 'Downloads')

def add_wrapped_text(pdf, text, width):
    items = [item.strip() for item in text.split(',')]
    for item in items:
        lines = wrap(item, width)
        for line in lines:
            pdf.cell(200, 10, txt=line, ln=True)
def add_section_title(pdf, title):
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True)

def add_bullet_point(pdf, text, indent_level=1):
    indent = ' ' * (indent_level * 4)
    pdf.cell(200, 10, txt=f"{indent}o {text}", ln=True)

def get_compliance_details_reports_service(org_id, resource_owner_id, selected_compliance):
    try:
        resource_id = db.session.query(Resources.resource_id).filter(Resources.resource_owner == resource_owner_id).first()
        if not resource_id:
            return None

        query = db.session.query(Compliance).filter(Compliance.org_id == org_id, Compliance.resource_id == resource_id[0], Compliance.selected_compliance == selected_compliance).all()

        if not query:
            return None
        
        compliance = Compliance.to_dict(query[0])
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        title = compliance.get('title', "Compliance Report")  
        pdf.cell(200, 10, txt="Compliance Report", ln=True, align='C')
        pdf.ln(5)  
        
        pdf.cell(200, 10, txt=f"Title: {title}", ln=True)
        pdf.ln(5)  

        generated_on = datetime.fromtimestamp(compliance['generated_on']).strftime('%d/%m/%Y')
        pdf.cell(200, 10, txt=f"Generated On: {generated_on}", ln=True)
        pdf.ln(10)  
        add_section_title(pdf, "Summary:")
        pdf.cell(200, 10, txt=f"   o  Total Checks: {compliance['total_checks']}", ln=True)
        compliant_checks = compliance['compliant_areas'] 
        non_compliant_checks = compliance['total_checks'] - compliant_checks
        pdf.cell(200, 10, txt=f"   o  Compliant: {compliant_checks}", ln=True)
        pdf.cell(200, 10, txt=f"   o  Non-Compliant: {non_compliant_checks}", ln=True)
        pdf.cell(200, 10, txt=f"   o  Critical Issues: {compliance['critical_issues']}", ln=True)
        pdf.ln(5)

        add_section_title(pdf, "Detailed Findings:")
        detailed_findings = compliance.get('detailed_findings', "No findings available.")
        
        if detailed_findings != "No findings available.":
            detailed_findings_cleaned = detailed_findings.replace("{", "").replace("}", "").replace("[", "").replace("]", "").replace('"', '').replace(":", "").split(',')
            for item in detailed_findings_cleaned:
                if item.strip(): 
                    add_bullet_point(pdf, item.strip())  
        else:
            add_bullet_point(pdf, "No findings available.")  

        pdf.ln(5)

        add_section_title(pdf, "Recommendations:")
        recommendations = compliance.get('recommendations', "No recommendations available.")
        
        if recommendations != "No recommendations available.":
            recommendations_cleaned = recommendations.replace("{", "").replace("}", "").replace("[", "").replace("]", "").replace('"', '').replace(":", "").split(',')
            for item in recommendations_cleaned:
                if item.strip():  
                    add_bullet_point(pdf, item.strip())  
        else:
            add_bullet_point(pdf, "No recommendations available.")  

        downloads_folder = get_downloads_folder()
        pdf_output_path = os.path.join(downloads_folder, f'compliance_report_{org_id}_{resource_owner_id}.pdf')
        pdf.output(pdf_output_path)

        with open(pdf_output_path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()

        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=compliance_report_{org_id}_{resource_owner_id}.pdf'

        return response

    except Exception as e:
        logger.error(f"Error fetching compliance details: {e}")
        return None





 
repo_path = "https://api.github.com/repos/sanketspcc/LGMVIP-TASK1/commits"

# repo_path = r"C:\Users\RaVaN\OneDrive\Desktop\MS 360\MS360-Backend\spectrum_360"



 
# Step 1: Run Bandit to check for security issues in Python code
def run_bandit():
    print("Running Bandit for security checks...")
    try:
        subprocess.run(["bandit", "-r", repo_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Bandit encountered an error: {e}")
    print("Bandit analysis complete.")
 
# Step 2: Run Gitleaks to find secrets in the Git repository
def run_gitleaks():
    print("Running Gitleaks to detect secrets...")
    try:
        subprocess.run(["gitleaks", "detect", "--source", repo_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Gitleaks encountered an error: {e}")
    print("Gitleaks analysis complete.")
 
# Step 3: Check GitHub security alerts (if the repo is hosted on GitHub)
# def check_github_security_alerts(repo_owner, repo_name, github_token):
#     print(f"Checking GitHub security alerts for {repo_owner}/{repo_name}...")

#     api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/vulnerability-alerts"
#     headers = {
#         "Authorization": f"token {github_token}",
#         "Accept": "application/vnd.github.dorian-preview+json"
#     }
#     response = requests.get(api_url, headers=headers)

#     if response.status_code == 204:
#         print("No security alerts found for this repository.")
#     elif response.status_code == 200:
#         print("Security alerts found:")
#         print(response.json())
#     else:
#         print(f"Failed to retrieve security alerts. Status code: {response.status_code}")
#         print(response.text)  # Optional: To see the response content for debugging




def check_github_security_alerts(repo_owner, repo_name, github_token):
    print(f"Checking GitHub security and code scanning alerts for {repo_owner}/{repo_name}...")

    ''' Headers for API requests '''
    
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    ''' Check vulnerability alerts '''

    vulnerability_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/vulnerability-alerts"
    vulnerability_response = requests.get(vulnerability_api_url, headers=headers)

    if vulnerability_response.status_code == 204:
        print("No vulnerability alerts found for this repository.")
    elif vulnerability_response.status_code == 200:
        print("Vulnerability alerts found:")
        print(vulnerability_response.json())
    else:
        print(f"Failed to retrieve vulnerability alerts. Status code: {vulnerability_response.status_code}")
        print(vulnerability_response.text)

    ''' Check code scanning alerts '''

    code_scanning_api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/code-scanning/alerts"
    code_scanning_response = requests.get(code_scanning_api_url, headers=headers)

    if code_scanning_response.status_code == 200:
        alerts = code_scanning_response.json()
        if alerts:
            print(f"{format_timestamp()} INF {len(alerts)} code scanning alerts found.")
            for alert in alerts:
                print(f"{format_timestamp()} WRN {alert['rule']['description']} - {alert['most_recent_instance']['location']['path']}")
        else:
            print(f"{format_timestamp()} INF No code scanning alerts found.")
    elif code_scanning_response.status_code == 403:
        print("Failed to retrieve code scanning alerts. Status code: 403 - Forbidden")
        print("The access token does not have the required permissions to access code scanning alerts.")
        print(code_scanning_response.json())  
    elif code_scanning_response.status_code == 404:
        print("Resource not found. The repository or alerts may not be accessible.")
    else:
        print(f"Failed to retrieve code scanning alerts. Status code: {code_scanning_response.status_code}")
        print(code_scanning_response.json())

def format_timestamp():
    from datetime import datetime
    return datetime.now().strftime("%I:%M%p")





















repo_path = "https://github.com/gradio-app/gradio"


import os
import subprocess
import shutil
from git import Repo
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scan_repo(repo_url, clone_dir='/tmp/repo_clone'):
    """
    Clone the repository, run Bandit scan, and clean up.
    """
    try:
        # Clone the repository
        if os.path.exists(clone_dir):
            shutil.rmtree(clone_dir)
        Repo.clone_from(repo_url, clone_dir)
        logger.info(f"Cloned repository: {repo_url}")
        
        # Run Bandit security scan
        result = subprocess.run(["bandit", "-r", clone_dir], capture_output=True, text=True)
        
        # Clean up the cloned repository
        shutil.rmtree(clone_dir)
        logger.info(f"Cleaned up cloned repository: {clone_dir}")

        if result.returncode == 0:
            return result.stdout
        else:
            return result.stderr

    except Exception as e:
        logger.error(f"Error during scanning: {e}")
        return str(e)
