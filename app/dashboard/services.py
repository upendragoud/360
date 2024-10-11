from collections import defaultdict
from app import db
from flask import json, jsonify
import requests
from app.assessments.models import Assessments,AssessmentDetails
from app.maturity_frameworks.models import MaturityFrameworks
from app.authentication.models import User, Profile
from app.resources.models import Resources, ResourceMembers, COEResourceOwner
from app.coe_team.models import COETeam
from app.recommendations.models import AssessmentRecommendations
from app.log_handler import get_logger
from app.organizations.models import Organizations
from sqlalchemy import desc, func
from time import strftime, localtime
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask_jwt_extended import get_jwt_identity
from collections import defaultdict
import calendar

load_dotenv()

logger = get_logger()

# ================= IDSM Part =================================================================================
API_KEY_HEADER = "X-API-KEY"
IDS_API_KEY = "b319d4400fa34dcb9af413c0aa008e3b21e00cca751945e7913dc10c87be97b6"
IDS_BASE_URL = os.getenv('IDSM_URL')
# IDS_BASE_URL = "http://backend-internal.idsm.com"

def request_service_token(service):
    headers = {
        API_KEY_HEADER: IDS_API_KEY
    }
    response = requests.post(f"{IDS_BASE_URL}/token/issue", json={"service_name": service}, headers=headers)
    if response.status_code != 200:
        return None
    return response.json()["token"]

def revoke_service_token(token):
    headers = {
        API_KEY_HEADER: IDS_API_KEY
    }
    response = requests.delete(f"{IDS_BASE_URL}/token/revoke", json={"token_value": token}, headers=headers)
    if response.status_code != 200:
        return None
    return jsonify(message='token revoked'), 200

def get_service_url(service_name):
    headers = {
        API_KEY_HEADER: IDS_API_KEY
    }
    response = requests.get(f"{IDS_BASE_URL}/service_discovery/{service_name}", headers=headers)
    if response.status_code != 200:
        logger.error(f"Failed to retrieve URL for {service_name} from service discovery.")
        return None
  
    return response.json().get("endpoint")
# ============= IDSM End ====================================================================================================



'''
Resource Owner
'''


def get_assessments_count():
    try:
        query = db.session.query(Assessments, User).filter(User.org_id == 1).filter(
            Assessments.assessor_user_id == User.user_id)
        assessments_count = query.count()
        return assessments_count
    except Exception as e:
        logger.error(f"Error fetching dashboard assessment count: {e}")
        return None


def get_last_assessment_date():
    try:
        query = db.session.query(Assessments.assessment_schedule_date).filter(User.org_id == 1).filter(
            Assessments.assessor_user_id == User.user_id).order_by(desc(Assessments.assessment_schedule_date))
        rows = query.limit(1).all()
        # last_assessment_date = strftime('%Y-%m-%d %H:%M:%S', localtime(rows[0][0]))
        last_assessment_date = strftime('%d %b %Y', localtime(rows[0][0]))
        return last_assessment_date
    except Exception as e:
        logger.error(f"Error fetching dashboard last assessment date: {e}")
        return None


def get_developers_count():
    try:
        query = db.session.query(User).filter(User.org_id == 1).filter(User.role_id == 4)
        developers_count = query.count()
        return developers_count
    except Exception as e:
        logger.error(f"Error fetching dashboard developers count: {e}")
        return None


# def get_recent_assessments():
#     try:
#         query = db.session.query(Assessments.score, Assessments.assessment_schedule_date).join(
#             MaturityFrameworks, MaturityFrameworks.model_id == Assessments.model_id).filter(
#             MaturityFrameworks.org_id == 1).order_by(desc(Assessments.assessment_schedule_date))
#         recent_assessments = query.limit(5).all()
#         item = {}
#         response = {}
#         output = []
#         column_names = query.statement.columns.keys()
#         total_score = 0.0
#         count = 0
#         trend = 0
#         prev_score = None
#         delta_shift = 0.0
#         percent_delta_shift = None
#         for i in range(len(recent_assessments)):
#             for j in range(len(recent_assessments[i])):
#                 # item[column_names[j]] = recent_assessments[i][j]
#                 if column_names[j] == 'score':
#                     count = count + 1
#                     total_score = total_score + recent_assessments[i][j]
#                     if prev_score is None:
#                         prev_score = recent_assessments[i][j]
#                     else:
#                         if prev_score < recent_assessments[i][j]:
#                             trend = 1
#                             if i == 1:
#                                 if percent_delta_shift is None:
#                                     delta_shift = prev_score - recent_assessments[i][j]
#                                     percent_delta_shift = (delta_shift / recent_assessments[i][j]) * 100
#                         else:
#                             trend = 0
#                             if i == 1:
#                                 if percent_delta_shift is None:
#                                     delta_shift = prev_score - recent_assessments[i][j]
#                                     percent_delta_shift = (delta_shift / recent_assessments[i][j]) * 100
#                         prev_score = recent_assessments[i][j]
#                     item[column_names[j]] = recent_assessments[i][j]
#                 else:
#                     item[column_names[j]] = strftime('%d %b %Y', localtime(recent_assessments[i][j]))
#             output.append(item)
#             item = {}
#         avg_score = str(round(total_score / count, 2))
#         response['recent_assessments'] = output[::-1]
#         response['avg_score'] = avg_score
#         response['trend'] = trend
#         response['trend_percentage'] = str(round(percent_delta_shift, 2))
#         response['last_assessment_score'] = output[0]['score']
#         return response
#     except Exception as e:
#         logger.error(f"Error fetching dashboard recent assessments: {e}")
#         return None


# def get_last_assessment_score():
#     try:
#         query = db.session.query(Assessments.score).filter(User.org_id == 1).filter(
#             Assessments.assessor_user_id == User.user_id).filter(MaturityFrameworks.org_id == User.org_id).filter(
#             Assessments.model_id == MaturityFrameworks.model_id).order_by(desc(Assessments.assessment_schedule_date))
#         rows = query.limit(2).all()
#         rows_count = len(rows)
#         percent_delta = 0.0
#         if rows_count > 1:
#             percent_delta = rows[0][0] / rows[1][0]
#         output = {'last_assessment_score': rows[0][0], 'percent_delta': percent_delta}
#         return output
#     except Exception as e:
#         logger.error(f"Error fetching dashboard last assessment score: {e}")
#         return None


# def get_last_framework_used():
#     try:
#         query = db.session.query(Assessments.assessment_id, MaturityFrameworks.name, MaturityFrameworks.tags).join(
#             Resources, Resources.resource_id == Assessments.resource_id).join(
#             MaturityFrameworks, MaturityFrameworks.model_id == Assessments.model_id).filter(
#             Resources.resource_id == 1).order_by(desc(Assessments.assessment_schedule_date))
#         rows = query.all()
#         # rows_count = len(rows)
#         # output = {'resource_templates_count': rows_count, 'last_template_used':rows[0][2].capitalize()}
#         output = rows[0][2].capitalize()
#         return output
#     except Exception as e:
#         logger.error(f"Error fetching count of models owned by resource: {e}")
#         return None


# def get_framework_count_used():
#     try:
#         query = db.session.query(MaturityFrameworks.model_id.distinct()).join(
#             Assessments, MaturityFrameworks.model_id == Assessments.model_id).join(
#             Resources, Resources.resource_id == Assessments.resource_id).join(COETeam,
#                                                                               Resources.coe_id == COETeam.team_id).filter(
#             Resources.resource_id == 1).order_by(desc(Assessments.assessment_schedule_date))
#         rows = query.all()
#         rows_count = len(rows)
#         return rows_count
#     except Exception as e:
#         logger.error(f"Error fetching count of models owned by resource: {e}")
#         return None


def get_admin_details():
    try:
        query = db.session.query(User.user_email, Profile.f_name, Profile.l_name).join(
            Profile, User.user_id == Profile.user_id).join(COETeam, User.user_id == COETeam.coe_admin_id).join(
            Resources, Resources.coe_id == COETeam.team_id).filter(Resources.resource_id == 1)
        admin_details = query.first()
        if admin_details is not None:
            column_names = query.statement.columns.keys()
            output = {}
            for i in range(len(column_names)):
                output[column_names[i]] = admin_details[i]
            return output
        else:
            return None
    except Exception as e:
        logger.error(f"Error fetching COE admin details: {e}")
        return None


def get_daterange_assessments(start_date, end_date):
    try:
        query = db.session.query(Assessments.assessment_id, Assessments.resource_id,
                                 Assessments.assessment_schedule_date).filter(Assessments.assessment_schedule_date >= start_date).filter(
            Assessments.assessment_schedule_date <= end_date)
        assessments = query.all()
        if assessments is not None:
            item = {}
            output = []
            column_names = query.statement.columns.keys()
            for i in range(len(assessments)):
                for j in range(len(assessments[i])):
                    item[column_names[j]] = assessments[i][j]
                output.append(item)
                item = {}
            return output
        else:
            return None
    except Exception as e:
        logger.error(f"Error fetching assessments in date range: {e}")
        return None


# def get_last_assessment_recommendation_details():
#     try:
#         # Get ID of recent assessment
#         query = db.session.query(Assessments.assessment_id, Assessments.assessment_schedule_date, MaturityFrameworks.name).join(
#             MaturityFrameworks, MaturityFrameworks.model_id == Assessments.model_id).filter(
#             MaturityFrameworks.org_id == 1).order_by(desc(Assessments.assessment_schedule_date))
#         assessments = query.limit(1).all()
#         last_assessment_id = assessments[0][0]
#         # Get total recommendations count and completed recommendations count
#         query = db.session.query(AssessmentRecommendations.recommendation_id,
#                                  AssessmentRecommendations.recommendation_description,
#                                  AssessmentRecommendations.recommendation_status).join(Assessments,
#                                                                                        Assessments.assessment_id == AssessmentRecommendations.assessment_id).join(
#             MaturityFrameworks, MaturityFrameworks.model_id == Assessments.model_id).filter(
#             MaturityFrameworks.org_id == 1).order_by(desc(Assessments.assessment_schedule_date)).filter(
#             Assessments.assessment_id == last_assessment_id)
#         recommendations = query.all()
#         recommendations_count = query.count()
#         if recommendations is not None:
#             response = {}
#             item = {}
#             output = []
#             column_names = query.statement.columns.keys()
#             completed_recommendations = 0
#             for i in range(len(recommendations)):
#                 for j in range(len(recommendations[i])):
#                     item[column_names[j]] = recommendations[i][j]
#                     if column_names[j] == "recommendation_status":
#                         if recommendations[i][j] != 0:
#                             completed_recommendations = completed_recommendations + 1
#                 output.append(item)
#                 item = {}
#             response['total'] = recommendations_count
#             response['list'] = output
#             response['completed'] = completed_recommendations
#             return response
#         else:
#             return None
#     except Exception as e:
#         logger.error(f"Error fetching assessments in date range: {e}")
#         return None


# *****************************
# Resource Owner main dashboard
# *****************************


def get_coe_stats(resource_owner_id):
    try:
        query = db.session.query(COETeam.coe_area, Assessments.score, Assessments.assessment_schedule_date,
                                 MaturityFrameworks.name, Resources.resource_name).join(Resources,
                                                                                        Assessments.resource_id == Resources.resource_id).join(
            COEResourceOwner, COEResourceOwner.coe_team_id == Resources.coe_id).join(COETeam,
                                                                                     COETeam.team_id == COEResourceOwner.coe_team_id).join(
            Organizations, COETeam.org_id == Organizations.org_id).join(User, User.org_id == COETeam.org_id).join(
            MaturityFrameworks, Assessments.model_id == MaturityFrameworks.model_id).filter(
            User.user_id == resource_owner_id).order_by(Assessments.assessment_schedule_date.desc())
        assessments = query.all()
        if assessments is not None:
            item = {}
            output = []
            column_names = query.statement.columns.keys()
            practice_areas = []
            # Get practice areas
            for i in range(len(assessments)):
                for j in range(len(assessments[i])):
                    item[column_names[j]] = assessments[i][j]
                    if column_names[j] == "coe_area":
                        practice_areas.append(assessments[i][j])
                output.append(item)
                item = {}
            sorted_assessments_score = sorted(output, key=lambda k: k.get('score', 0), reverse=True)
            practice_areas = list(set(practice_areas))

            # Assessment scores of prev 4 quarters
            sorted_assessments_coe = sorted(output, key=lambda k: k.get('coe_area', 0), reverse=True)
            count = 0
            chart_data = {}
            coe_data = []
            for i in range(len(practice_areas)):
                for j in range(len(sorted_assessments_coe)):
                    if practice_areas[i] == sorted_assessments_coe[j]['coe_area']:
                        if count < 4:
                            coe_data.append(sorted_assessments_coe[j])
                        chart_data[practice_areas[i]] = coe_data
                        count = count + 1
                coe_data = []
                count = 0

            # Recent assessments
            sorted_assessments_date = sorted(output, key=lambda k: k.get('assessment_schedule_date', 0), reverse=True)
            recent_assessments_list = {}
            coe_data = []
            count = 0
            for i in range(len(practice_areas)):
                for j in range(len(sorted_assessments_date)):
                    if practice_areas[i] == sorted_assessments_date[j]['coe_area']:
                        if count < 1:
                            coe_data.append(sorted_assessments_date[j])
                        recent_assessments_list[practice_areas[i]] = coe_data
                        count = count + 1
                coe_data = []
                count = 0

            # Peer comparison
            sorted_assessments_score = sorted(output, key=lambda k: k.get('score', 0), reverse=True)
            highest_assessment_scores = {}
            coe_data = []
            count = 0
            for i in range(len(practice_areas)):
                for j in range(len(sorted_assessments_score)):
                    if practice_areas[i] == sorted_assessments_score[j]['coe_area']:
                        if count < 1:
                            coe_data.append(sorted_assessments_score[j])
                        highest_assessment_scores[practice_areas[i]] = coe_data
                        count = count + 1
                coe_data = []
                count = 0
            peer_scores = {}
            peer_comp = {}
            for i in range(len(practice_areas)):
                for j in highest_assessment_scores.keys():
                    if practice_areas[i] == j:
                        peer_scores['recent_score'] = recent_assessments_list[j][0]['score']
                        peer_scores['highest_score'] = highest_assessment_scores[j][0]['score']
                peer_comp[practice_areas[i]] = peer_scores

            response = {'highest_maturity_score': sorted_assessments_score[0],
                        'lowest_maturity_score': sorted_assessments_score[-1],
                        'current_assessment_scores': recent_assessments_list,
                        'chart_data': chart_data,
                        'peer_comparison': peer_comp
                        }
            return response
        else:
            return None
    except Exception as e:
        logger.error(f"Error fetching assessments and details: {e}")
        return None


def get_lead_lag_stats(resource_owner_id):
    try:
        # List all resources in all COE, in which resource owner owns a resource
        subquery = db.session.query(COETeam.team_id).join(Resources, Resources.coe_id == COETeam.team_id).filter(
            Resources.resource_owner == resource_owner_id)
        query = db.session.query(Resources.resource_name, Resources.resource_owner, COETeam.coe_area, Assessments.score,
                                 Assessments.assessment_schedule_date).join(COETeam, Resources.community_id == COETeam.team_id).join(
            Assessments, Resources.resource_id == Assessments.resource_id).filter(COETeam.team_id.in_(subquery))
        resources = query.all()
        if resources is not None:
            item = {}
            output = []
            column_names = query.statement.columns.keys()
            practice_areas = []
            # Get practice areas
            for i in range(len(resources)):
                for j in range(len(resources[i])):
                    item[column_names[j]] = resources[i][j]
                    if column_names[j] == "coe_area":
                        practice_areas.append(resources[i][j])
                output.append(item)
                item = {}
            practice_areas = list(set(practice_areas))
            # Assessment scores
            sorted_assessments_coe = sorted(output, key=lambda k: k.get('coe_area', 0), reverse=True)
            count = 0
            chart_data = {}
            coe_data = []
            for i in range(len(practice_areas)):
                for j in range(len(sorted_assessments_coe)):
                    if practice_areas[i] == sorted_assessments_coe[j]['coe_area']:
                        coe_data.append(sorted_assessments_coe[j])
                        chart_data[practice_areas[i]] = coe_data
                        count = count + 1
                coe_data = []
                count = 0
            sorted_coe_resources = {}
            for i in range(len(practice_areas)):
                for j in range(len(chart_data[practice_areas[i]])):
                    sorted_coe_resources[practice_areas[i]] = sorted(chart_data[practice_areas[i]], key=lambda k: k.get(
                        chart_data[practice_areas[i]][j]['resource_name'], 0), reverse=True)

            '''
            count = 0
            coe_resources = {}
            coe_data = []
            for i in range(len(practice_areas)):
                for j in range(len(sorted_coe_resources)):
                    if practice_areas[i] == sorted_coe_resources[j]['coe_area']:
                        coe_data.append(sorted_coe_resources[j])
                        coe_resources[practice_areas[i]] = coe_data
                        count = count + 1
                coe_data = []
                count = 0
            '''

            '''
            for i in range(len(practice_areas)):
                for j in range(len(sorted_coe_resources)):
                    for k in range(len(sorted_coe_resources[practice_areas[i]])):
                        if practice_areas[i] == sorted_coe_resources[j]['coe_area']:
                            coe_data.append(sorted_coe_resources[j])
                            # coe_resources[practice_areas[i]][k]['resource_name'] = coe_data
                            coe_resources['resource_name'] = coe_data
                            count = count + 1
                    coe_data = []
                    count = 0
            '''
            count = 0
            coe_data = {}
            coe_resources = []
            coe_resources_name_obj = {}
            coe_resources_obj = {}

            resource_name = ""
            for i in range(len(practice_areas)):
                for j in range(len(sorted_coe_resources)):
                    for k in range(len(sorted_coe_resources[practice_areas[i]])):
                        if resource_name == sorted_coe_resources[practice_areas[i]][k]['resource_name']:
                            # print(sorted_coe_resources[practice_areas[i]][k], flush=True)
                            coe_resources.append(sorted_coe_resources[practice_areas[i]][k])
                        else:
                            coe_resources = []
                            resource_name = sorted_coe_resources[practice_areas[i]][k]['resource_name']
                            coe_resources.append(sorted_coe_resources[practice_areas[i]][k])
                        # print(coe_resources, flush=True)
                    coe_resources_obj[sorted_coe_resources[practice_areas[i]][k]['resource_name']] = coe_resources
                   
                    coe_resources = []
                coe_data[practice_areas[i]] = coe_resources_obj
                coe_resources_obj = {}
            # print(coe_data, flush=True)
        return None
    except Exception as e:
        logger.error(f"Error fetching leading and lagging stats: {e}")
        return None
    
# Number of subscribers of each community
def get_communities_subscriber():
    service_token = request_service_token("Spectra_Hub")

    if not service_token:
        return jsonify(message="Failed to retrieve service token"), 400

    service_url = get_service_url("Spectra_Hub")
    if not service_url:
        return jsonify(message="Failed to retrieve service URL from service discovery"), 400

    headers = {
        "Authorization": f"Bearer {service_token}",
        "X-Service-Name": f"Spectra_Hub"
    }

    # response = requests.get(f"{service_url}/communities/list", headers=headers)
    response = requests.get(f"{service_url}/communities/comm_sub/list", headers=headers)
    revoke_service_token(service_token)
    if response.status_code == 200:    
        comm_sub = response.json()
        community_user_list = {}
        for entry in comm_sub:
            community_id = entry["community_id"]
            user_id = entry["user_id"]
            if community_id in community_user_list:
                community_user_list[community_id].append(user_id)
            else:
                community_user_list[community_id] = [user_id]
        
        result = [{"community_id": key, "subscribers_list": value} for key, value in community_user_list.items()]
        return result,   200
    return "No data available", 404


# get subscribed communities
def get_subscribed_communities(resource_id):
   
    service_token = request_service_token("Spectra_Hub")
   
    if not service_token:
        return "Failed to retrieve service token", 400

    service_url = get_service_url("Spectra_Hub")
    if not service_url:
        return jsonify(message="Failed to retrieve service URL from service discovery"), 400

    headers = {
        "Authorization": f"Bearer {service_token}",
        "X-Service-Name": f"Spectra_Hub"
    }
    response = requests.get(f"{service_url}/communities/comm_sub/{resource_id}", headers=headers)
    revoke_service_token(service_token)
   
    if response.status_code == 200:
        return response, 200
    return "No subscriptions data available",    404



# search by community_name or practice_area
def search_community_practice_area(keyword):
    service_token = request_service_token("Spectra_Hub")
    if not service_token:
        return jsonify(message="Failed to retrieve service token"), 400

    service_url = get_service_url("Spectra_Hub")
    if not service_url:
        return jsonify(message="Failed to retrieve service URL from service discovery"), 400

    headers = {
        "Authorization": f"Bearer {service_token}",
        "X-Service-Name": f"Spectra_Hub"
    }

    response = requests.get(f"{service_url}/communities/search/{keyword}", headers=headers)
    revoke_service_token(service_token)
    # print(response.json())
    if response.status_code == 200:
        return response,    200
    return "No matching communities available",  404


# get maturity score from assessments
def get_maturity_score():
    try:
        query = db.session.query(Resources.community_id,func.avg(Assessments.score).label('maturity_score')).join(Assessments,Resources.resource_id == Assessments.resource_id)
        query = query.group_by(Resources.community_id)
        results = query.all()
       
        list_of_scores = []
        for community_id, maturity_score in results:
            scores = {}
            scores['community_id'] = community_id
            scores['maturity_score'] = round(maturity_score,1)
            list_of_scores.append(scores)
        return list_of_scores,  200
    except Exception as e:
        logger.error(f"Error :{e}")
        return "No score available",    404
    

def get_maturity_score_by_community_id(community_id):
    try:
        query = db.session.query(Resources.community_id,func.avg(Assessments.score).label('maturity_score')).join(Assessments,Resources.resource_id == Assessments.resource_id)
        query = query.filter(Resources.community_id == community_id)
        results = query.first()
        scores = {}
        for community_id, maturity_score in results:
            scores['community_id'] = community_id
            scores['maturity_score'] = round(maturity_score,1)
        return scores,  200
    except Exception as e:
        logger.error(f"Error :{e}")
        return "No score available",    404

# get community by id
def get_community_by_id_service(community_id):
    service_token = request_service_token("Spectra_Hub")
    if not service_token:
        return jsonify(message="Failed to retrieve service token"), 400

    service_url = get_service_url("Spectra_Hub")
    if not service_url:
        return jsonify(message="Failed to retrieve service URL from service discovery"), 400

    headers = {
        "Authorization": f"Bearer {service_token}",
        "X-Service-Name": f"Spectra_Hub"
    }
    response = requests.get(f"{service_url}/communities/{community_id}", headers=headers)
    # response = requests.get(f"{service_url}/communities/details/{community_id}", headers=headers)
    revoke_service_token(service_token)
    if response.status_code == 200:
        return response,    200
    return "No community to display",    404


# create Community subscription 
def create_community_subscription_service(data):
    service_token = request_service_token("Spectra_Hub")
    if not service_token:
        return jsonify(message="Failed to retrieve service token"), 400

    service_url = get_service_url("Spectra_Hub")
    if not service_url:
        return jsonify(message="Failed to retrieve service URL from service discovery"), 400

    headers = {
        "Authorization": f"Bearer {service_token}",
        "X-Service-Name": f"Spectra_Hub"
    }
    response = requests.post(f"{service_url}/communities/comm_sub/create", json=data, headers=headers)
    revoke_service_token(service_token)
    if response.status_code == 200:
        return response.json(),    200
    return "Unable to subscribe",    404


# delete Community subscription 
def delete_community_subscription_service(user_id, community_id):
    service_token = request_service_token("Spectra_Hub")
    if not service_token:
        return jsonify(message="Failed to retrieve service token"), 400

    service_url = get_service_url("Spectra_Hub")
    if not service_url:
        return jsonify(message="Failed to retrieve service URL from service discovery"), 400

    headers = {
        "Authorization": f"Bearer {service_token}",
        "X-Service-Name": f"Spectra_Hub"
    }
    response = requests.delete(f"{service_url}/communities/comm_sub/{user_id}/{community_id}", headers=headers)
    revoke_service_token(service_token)
    if response.status_code == 200:
        return response.json(),    200
    return "Unable to unsubscribe",    404


# get templates billing for particular user by user_id
def get_billing_service(user_id):
    service_token = request_service_token("Spectra_Store")
    if not service_token:
        return jsonify(message="Failed to retrieve service token"), 400

    service_url = get_service_url("Spectra_Store")
    if not service_url:
        return jsonify(message="Failed to retrieve service URL from service discovery"), 400

    headers = {
        "Authorization": f"Bearer {service_token}",
        "X-Service-Name": f"Spectra_Hub"
    }

    response = requests.post(f"{service_url}/tempbill/billing", json=user_id, headers=headers)
    revoke_service_token(service_token)
    if response.status_code == 200:
        return response,   200
    return "No bills to display", 404

def get_current_score_service(user_id,practice_area,resource_id):
    try:

        query = db.session.query(Assessments).filter(
            Assessments.practice_area.like(practice_area),
            Assessments.resource_id == resource_id,
            Assessments.assessment_status==4,
            Assessments.is_deleted == 0
        )
       
        latest_assessments = query.order_by(Assessments.assessment_end_date.desc()).first()

        if latest_assessments:
            score = latest_assessments.score
            return {
                    "score": score,
                    "framework_used":latest_assessments.framework_name,
                    "assessment_id":latest_assessments.assessment_id,
                    "assessment_taken":latest_assessments.assessment_end_date
                    }
        return None
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return {"error": "An error occurred while fetching the scores. Please try again later."}


#get the highest maturity score by practice area
def get_highest_maturity_score_by_practice_area(practice_area):
    try:
        # Get the current user's details
        user_details = get_jwt_identity()
        user_id = user_details.get('user_id')

        # Fetching resource_id
        resource_id = db.session.query(Resources.resource_id).filter(Resources.resource_owner == user_id).scalar()

        if not resource_id:
            return {"error": "Resource not found"}, 404

        # Constructing the query to calculate the highest maturity score
        query = db.session.query(
            Assessments.practice_area,
            func.max(Assessments.score).label('maturity_score')
        ).join(Resources, Resources.resource_id == Assessments.resource_id).filter(
            Assessments.practice_area == practice_area,
            Resources.resource_id == resource_id
        )

        # Fetching the first result which will be the highest score
        result = query.first()

        if result:
            # Processing the result into a dictionary
            highest_score = {
                'practice_area': result.practice_area,
                'highest_maturity_score': round(result.maturity_score, 1)
            }
            return highest_score
        else:
            return {"error": "No score available"}, 404

    except Exception as e:
        # Logging and returning error message
        logger.error(f"Error: {e}")
        return {"error": "An error occurred while fetching the highest maturity score. Please try again later."}, 500
  

#get the lowest maturity score by practice area 
def get_lowest_maturity_score_by_practice_area(practice_area):
    try:
        user_details = get_jwt_identity()
        user_id = user_details.get('user_id')

        resource_id = db.session.query(Resources.resource_id).filter(Resources.resource_owner == user_id).scalar()

        if not resource_id:
            return {"error": "Resource not found"}, 404

        query = db.session.query(
            Assessments.practice_area,
            func.min(Assessments.score).label('maturity_score')
        ).join(Resources, Resources.resource_id == Assessments.resource_id).filter(
            Assessments.practice_area == practice_area,
            Resources.resource_id == resource_id
        )

        result = query.first()

        if result:
            lowest_score = {
                'practice_area': result.practice_area,
                'lowest_maturity_score': round(result.maturity_score, 1)
            }
            return lowest_score
        else:
            return {"error": "No score available"}, 404

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"error": "An error occurred while fetching the lowest maturity score. Please try again later."}, 500
 

def get_recommendations_count():
    user_details = get_jwt_identity()
    user_id = user_details.get('user_id')
    practice_area = user_details.get('practice_area')
    resource_id = db.session.query(Resources.resource_id).filter(Resources.resource_owner == user_id).scalar()
    result = db.session.query(
                            Assessments.assessment_id,Assessments.practice_area
                        ).filter(
                            Assessments.assessment_status == 4,Assessments.resource_id==resource_id,Assessments.practice_area==practice_area 
                        ).order_by(
                            Assessments.assessment_end_date.desc()
                        ).first()
    if result:
        assessment_id = result.assessment_id
        recommendations_count = db.session.query(func.count(AssessmentRecommendations.recommendation_id)
                                ).filter(
                                    AssessmentRecommendations.recommendation_status == 4,
                                    AssessmentRecommendations.assessment_id==assessment_id
                                ).scalar()
        
        recommendations_pending = db.session.query(func.count(AssessmentRecommendations.recommendation_id)
                                ).select_from(Assessments).join(
                                    AssessmentRecommendations,
                                    Assessments.assessment_id == AssessmentRecommendations.assessment_id
                                ).filter(
                                    AssessmentRecommendations.assessment_id==assessment_id,
                                    AssessmentRecommendations.recommendation_status != 4
                                ).scalar()
        recommendations = {
            'completed_recommendations': recommendations_count,
            'pending_recommendations':recommendations_pending
        }
    return recommendations


def epoch_to_datetime(epoch):
    return datetime.fromtimestamp(epoch)

def get_quarterly_maturity_scores(practice_area):
    try:
        user_details = get_jwt_identity()
        user_id = user_details.get('user_id')
        resource_id = db.session.query(Resources.resource_id).filter(Resources.resource_owner == user_id).scalar()

        if not resource_id:
            logger.info("No resource found for the user.")
            return {"error": "No resource found for the user."}

        current_date = datetime.now()
        current_year = current_date.year
        current_quarter = (current_date.month - 1) // 3 + 1

        if current_quarter == 1:
            start_year = current_year - 1
            start_quarter = 2
        elif current_quarter == 2:
            start_year = current_year - 1
            start_quarter = 3
        elif current_quarter == 3:
            start_year = current_year - 1
            start_quarter = 4
        else:
            start_year = current_year
            start_quarter = current_quarter - 3

        end_date = current_date.timestamp()

        if start_quarter == 1:
            start_date = datetime(start_year, 1, 1).timestamp()
        elif start_quarter == 2:
            start_date = datetime(start_year, 4, 1).timestamp()
        elif start_quarter == 3:
            start_date = datetime(start_year, 7, 1).timestamp()
        else:
            start_date = datetime(start_year, 10, 1).timestamp()

        assessments = db.session.query(
            Assessments.assessment_end_date,
            Assessments.score
        ).filter(
            Assessments.practice_area == practice_area,
            Assessments.resource_id == resource_id,
            Assessments.assessment_end_date >= start_date,
            Assessments.assessment_end_date <= end_date,
            Assessments.is_deleted == 0
        ).all()

        quarterly_scores = defaultdict(lambda: {'total_score': 0, 'count': 0})

        # Function to get the quarter for a given date
        def get_quarter(date):
            if date.month <= 3:
                return 1
            elif date.month <= 6:
                return 2
            elif date.month <= 9:
                return 3
            else:
                return 4

        for assessment in assessments:
            assessment_end_date = datetime.fromtimestamp(assessment.assessment_end_date)
            year = assessment_end_date.year
            quarter = get_quarter(assessment_end_date)
            key = (year, quarter)
            quarterly_scores[key]['total_score'] += assessment.score
            quarterly_scores[key]['count'] += 1

        maturity_score_overview = []
        quarters_processed = 0

        for year in range(current_year, current_year - 2, -1):
            for quarter in range(4, 0, -1):
                if quarters_processed == 4:
                    break
                key = (year, quarter)
                if key in quarterly_scores:
                    total_score = quarterly_scores[key]['total_score']
                    count = quarterly_scores[key]['count']
                    average_score = round(total_score / count, 1) if count > 0 else None
                    overview_entry = {
                        "date": f"{year} Q{quarter}",
                        "score": average_score
                    }
                    maturity_score_overview.append(overview_entry)
                    quarters_processed += 1
            if quarters_processed == 4:
                break

        return maturity_score_overview

    except Exception as e:
        logger.error(f"Error fetching quarterly maturity scores: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while fetching the quarterly maturity scores. Please try again later."}), 500

def get_peer_comparison(user_id,practice_area):
    try:
        # Get the current user's latest assessment score in the specified practice area
        user_latest_data = db.session.query(
            Assessments.score,
            Resources.resource_name,
            Resources.resource_id,
            Organizations.org_name
        ).join(Resources, Resources.resource_id == Assessments.resource_id
        ).join(Organizations,Organizations.org_id==Resources.org_id).filter(
            Resources.resource_owner == user_id,
            Assessments.practice_area == practice_area
        ).order_by(Assessments.assessment_end_date.desc()).first()
        print("user_latest_data",user_latest_data)

        user_latest_score = user_latest_data.score if user_latest_data else None
        user_resource_name = user_latest_data.resource_name if user_latest_data else None
        user_resource_id = user_latest_data.resource_id if user_latest_data else None
        user_org = user_latest_data.org_name if user_latest_data else None
        # Subquery to get the latest assessment end date for each resource in the same practice area
        latest_assessments_subquery = db.session.query(
            Assessments.resource_id,
            func.max(Assessments.assessment_end_date).label('latest_assessment_date')
        ).join(Resources, Resources.resource_id == Assessments.resource_id).filter(
            Assessments.practice_area == practice_area
        ).group_by(Assessments.resource_id).subquery()

        # latest score for each resource
        industry_scores = db.session.query(
                Assessments.resource_id,
                Assessments.score,
                Resources.resource_owner,
                Resources.resource_name,
                Organizations.org_name
            ).join(Resources, Resources.resource_id == Assessments.resource_id
            ).join(Organizations, Organizations.org_id == Resources.org_id
            ).join(latest_assessments_subquery,
                (Assessments.resource_id == latest_assessments_subquery.c.resource_id) &
                (Assessments.assessment_end_date == latest_assessments_subquery.c.latest_assessment_date)
            ).order_by(Assessments.score.desc()).all()
       
        # Calculate the average score of the industry
        other_scores = [score for _, score, _, _,_ in industry_scores]
        industry_avg_score = round(sum(other_scores) / len(other_scores),2) if other_scores else None

        # Determine the rank of the user's resource and find peer comparison
        user_rank = None
        peer_resource_name = None
        peer_resource_score = None
        top_performer_name = None
        top_performer_score = None

        for i, (resource_id, score, _, resource_name,org_name) in enumerate(industry_scores):
            if i == 0:
                top_performer_name = resource_name
                top_performer_score = score
                top_performer_org = org_name
            if i == 1:
                second_top_performer_name = resource_name
                second_top_performer_score = score
                second_top_performer_org = org_name
            if resource_id == user_resource_id:
                user_rank = i + 1  # Rank is index + 1

        # If the user's resource is the top performer, set the second top performer as peer resource
        if user_resource_id == industry_scores[0][0]:
            peer_resource_name = second_top_performer_name
            peer_resource_score = second_top_performer_score
            peer_resource_org = second_top_performer_org
        else:
            peer_resource_name = top_performer_name
            peer_resource_score = top_performer_score
            peer_resource_org = top_performer_org
                
        return {
            'user_resource_name':user_resource_name,           
            'user_latest_score': user_latest_score,
            'user_org':user_org,
            "peer_resource":peer_resource_name,
            "peer_resource_score":peer_resource_score,
            "peer_resource_org":peer_resource_org,
            'top_resource':top_performer_name,
            'top_score': top_performer_score,  
            'top_org': top_performer_org,
            'percentile': user_rank,
            'industry_avg_score': industry_avg_score
        }
  
    except Exception as e:
        logger.error(f"Error getting peer comparison: {e}")
        return None


def get_quarterly_assessments(practice_area):
    try:
        user_details = get_jwt_identity()
        user_id = user_details.get('user_id')
        resource_id = db.session.query(Resources.resource_id).filter(Resources.resource_owner == user_id).scalar()

        if not resource_id:
            logger.info("No resource found for the user.")
            return {"error": "No resource found for the user."}

        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month

        # Determine the current quarter
        if current_month <= 3:
            current_quarter = 1
        elif current_month <= 6:
            current_quarter = 2
        elif current_month <= 9:
            current_quarter = 3
        else:
            current_quarter = 4

        # Define the start date for the last four quarters including the current quarter
        if current_quarter == 1:
            start_date = datetime(current_year - 1, 4, 1)
        elif current_quarter == 2:
            start_date = datetime(current_year - 1, 7, 1)
        elif current_quarter == 3:
            start_date = datetime(current_year - 1, 10, 1)
        else:
            start_date = datetime(current_year - 1, 1, 1)

        start_date_timestamp = start_date.timestamp()
        end_date_timestamp = current_date.timestamp()

        assessments = db.session.query(
            Assessments.assessment_id,
            Assessments.assessment_end_date
        ).filter(
            Assessments.practice_area == practice_area,
            Assessments.resource_id == resource_id,
            Assessments.assessment_end_date >= start_date_timestamp,
            Assessments.assessment_end_date <= end_date_timestamp,
            Assessments.is_deleted == 0
        ).all()

        quarterly_counts = defaultdict(int)

        # Function to get the quarter for a given date
        def get_quarter(date):
            if date.month <= 3:
                return 1
            elif date.month <= 6:
                return 2
            elif date.month <= 9:
                return 3
            else:
                return 4

        for assessment in assessments:
            assessment_end_date = datetime.fromtimestamp(assessment.assessment_end_date)
            year = assessment_end_date.year
            quarter = get_quarter(assessment_end_date)
            quarterly_counts[(year, quarter)] += 1

        assessments_overview = []
        quarters = [(current_year - 1, q) for q in range(1, 5)] + [(current_year, q) for q in range(1, current_quarter + 1)]
        quarters = quarters[-4:]

        for year, quarter in quarters:
            assessment_count = quarterly_counts[(year, quarter)]
            overview_entry = {
                "date": f"{year} Q{quarter}",
                "assessment_count": assessment_count
            }
            assessments_overview.append(overview_entry)

        return assessments_overview

    except Exception as e:
        logger.error(f"Error fetching quarterly assessments: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while fetching the quarterly assessments. Please try again later."}), 500

def get_benchmarking_comparison(practice_area):
    try:
        user_details = get_jwt_identity()
        user_id = user_details['user_id']
        user_org = user_details['account_id']

        org_avg_score_query = db.session.query(
            func.avg(Assessments.score)
        ).join(Resources, Resources.resource_id == Assessments.resource_id).filter(
            Resources.org_id == user_org,
            Assessments.practice_area == practice_area,
            Assessments.is_deleted == 0
        ).scalar()

        org_avg_score = round(org_avg_score_query, 1) if org_avg_score_query else None

        industry_avg_score_query = db.session.query(
            func.avg(Assessments.score)
        ).join(Resources, Resources.resource_id == Assessments.resource_id).filter(
            Resources.org_id != user_org,
            Assessments.practice_area == practice_area,
            Assessments.is_deleted == 0
        ).scalar()

        industry_avg_score = round(industry_avg_score_query, 1) if industry_avg_score_query else None
        
        return {
            'org_avg_score': org_avg_score,
            'industry_avg_score': industry_avg_score
        }
    except Exception as e:
        logger.error(f"Error fetching benchmarking comparison: {e}")
        return jsonify({"error": "An error occurred while fetching the benchmarking comparison. Please try again later."}), 500

def get_user_profile(practice_area):
    try:
        user_details = get_jwt_identity()
        user_id = user_details['user_id']
        user_org = user_details['account_id']
        last_login = user_details['last_login']
        resourse = db.session.query(Resources.resource_name).filter(Resources.resource_owner==user_id).scalar()
        profile = db.session.query(Profile.f_name,Profile.l_name).filter(Profile.user_id==user_id).first()

        community_area = practice_area
        result = {
            "user_id": user_id,
            "user_org": user_org,
            "resource": resourse,
            "community_area": community_area,
            "user_name":f"{profile.f_name} {profile.l_name}",
            "last_login":last_login
        }
        
        return result
    except Exception as e:
        logger.error(f"Error fetching user details:{e}")
        return jsonify({"error":"An error occured while fetching user_details"})
    
def get_knowledge_area_scores(practice_area):
    try:
        user_details = get_jwt_identity()
        user_id = user_details['user_id']
        
        resource_id = db.session.query(Resources.resource_id).filter(Resources.resource_owner == user_id).scalar()
        
        assessment = db.session.query(Assessments).filter(
            Assessments.resource_id == resource_id,Assessments.practice_area==practice_area
            # Assessments.practice_area == practice_area
        ).order_by(Assessments.assessment_end_date.desc()).first()
        assessment_id = assessment.assessment_id

        area_scores_list = db.session.query(AssessmentDetails.area_scores).filter(
            AssessmentDetails.assessment_id == assessment_id
        ).scalar()
        
        return json.loads(area_scores_list)

    except Exception as e:
        logger.error(f"error while fetching area scores:{e}")
        return None

def get_quarter(month):
    """Returns the quarter (Q1, Q2, Q3, Q4) for a given month."""
    if month in [1, 2, 3]:
        return 'Q1'
    elif month in [4, 5, 6]:
        return 'Q2'
    elif month in [7, 8, 9]:
        return 'Q3'
    else:
        return 'Q4'

def get_last_four_quarters():
    """Returns a list of the last four quarters in the format [(quarter, year), ...]."""
    current_date = datetime.utcnow()
    current_year = current_date.year
    current_quarter = get_quarter(current_date.month)

    # Map quarter names to numbers for easier manipulation
    quarter_map = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}
    reverse_quarter_map = {1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4'}

    # Get current quarter number
    current_quarter_num = quarter_map[current_quarter]

    # Collect last four quarters, moving backwards in time
    last_four_quarters = []
    for i in range(4):
        # If current_quarter_num goes below 1, we move to Q4 of the previous year
        quarter_num = (current_quarter_num - i - 1) % 4 + 1
        year = current_year - (current_quarter_num - i - 1) // 4
        last_four_quarters.append((reverse_quarter_map[quarter_num], year))

    return last_four_quarters

def get_maturity_assessment_progression( resource_id,practice_area):
    try:
        # Query to get all assessments for a specific resource, ordered by the assessment_end_date
        previous_assessments = db.session.query(
            Assessments.assessment_id,
            Assessments.score,
            Assessments.assessment_end_date
        ).filter(
            Assessments.resource_id == resource_id,
            Assessments.practice_area == practice_area,
            Assessments.assessment_status == 3
        ).order_by(
            Assessments.assessment_end_date.desc()
        ).all()

        if not previous_assessments:
            return None

        # Get the last four quarters
        last_four_quarters = get_last_four_quarters()

        # Initialize dictionary to store assessments grouped by quarter and year
        assessments_by_quarter = defaultdict(lambda: {"months": [], "scores": [], "highScore": None, "currentScore": None, "improvement": None})

        # To keep track of the last assessment of each month
        last_assessment_by_month = {}

        # Iterate through the assessments and store the last assessment for each month
        for assessment in previous_assessments:
            # Convert the epoch timestamp to a datetime object
            assessment_end_date = datetime.fromtimestamp(assessment.assessment_end_date)
            year = assessment_end_date.year
            month = assessment_end_date.month

            # Identify the quarter (Q1, Q2, Q3, Q4) based on the month
            quarter = get_quarter(month)
            quarter_key = f"{quarter} {year}"

            # Only consider assessments within the last four quarters
            if (quarter, year) in last_four_quarters:
                # Store the latest assessment per month (for the last day of the month)
                if (year, month) not in last_assessment_by_month:
                    last_assessment_by_month[(year, month)] = {
                        "month": calendar.month_abbr[month],
                        "score": assessment.score
                    }

        # Now organize the data by quarters
        for (year, month), data in last_assessment_by_month.items():
            quarter = get_quarter(month)
            quarter_key = f"{quarter} {year}"

            assessments_by_quarter[quarter_key]["months"].append(data["month"])
            assessments_by_quarter[quarter_key]["scores"].append(data["score"])

        # Calculate highScore, currentScore, and improvement for each quarter
        for quarter_key, data in assessments_by_quarter.items():
            if data["scores"]:
                data["highScore"] = max(data["scores"])  # Highest score in the quarter
                data["currentScore"] = data["scores"][-1]  # Last score in the quarter
                data["improvement"] = round(data["currentScore"] - data["scores"][0], 2)  # Improvement from the first score in the quarter

        # Only return data for the last four quarters
        return {qk: data for qk, data in assessments_by_quarter.items() if qk in [f"{q} {y}" for q, y in last_four_quarters]}

    except Exception as e:
        logger.error(f"Error fetching previous assessments: {e}")
        return None


    
def get_recommendations_by_user(practice_area,resource_id):
    try:
        latest_assessment = db.session.query(
            Assessments.assessment_id
        ).filter(
            Assessments.practice_area==practice_area,
            Assessments.is_deleted==0,
            Assessments.resource_id==resource_id,
            Assessments.assessment_status==4
        ).order_by(
            Assessments.assessment_end_date.desc()  
        ).first()
 
        if not latest_assessment:
            return None
        
        recommendations = db.session.query(
            AssessmentRecommendations.recommendation_title,
            AssessmentRecommendations.recommendation_description,
            AssessmentRecommendations.recommendation_priority,
            AssessmentRecommendations.recommendation_status,
            AssessmentRecommendations.recommendation_dead_line
        ).filter(
            AssessmentRecommendations.assessment_id == latest_assessment.assessment_id
        ).all()
 
        if not recommendations:
            return None
 
        recommendation_list = [
            {
                "recommendation_title": rec.recommendation_title,
                "recommendation_description":rec.recommendation_description,
                "recommendation_priority":rec.recommendation_priority
            } for rec in recommendations
        ]
 
        return recommendation_list
 
    except Exception as e:
        logger.error(f"Error fetching recommendations: {e}")
        return None

# *****************************
# Developer Dashboard
# *****************************


def get_dev_uname(user_id):
    try:
        query = db.session.query(Profile.f_name, Profile.l_name, Profile.designation, Profile.user_pic).filter(
            Profile.user_id == user_id)
        profile = query.first()
        if profile is not None:
            column_names = query.statement.columns.keys()
            output = {}
            for i in range(len(column_names)):
                output[column_names[i]] = profile[i].capitalize()
            return output
        else:
            return None
    except Exception as e:
        logger.error(f"Error fetching assessments in date range: {e}")
        return None


def get_dev_score_cur_prev(user_id):
    try:
        subquery = db.session.query(ResourceMembers.resource_id).filter(ResourceMembers.resource_member == user_id)
        query = db.session.query(Assessments.assessment_id, Assessments.assessment_schedule_date, Assessments.score).filter(
            Assessments.resource_id.in_(subquery)).filter(Assessments.assessment_status == 3).order_by(
            desc(Assessments.assessment_schedule_date))
        assessments = query.all()
        if assessments is not None:
            item = {}
            output = []
            column_names = query.statement.columns.keys()
            for i in range(len(assessments)):
                for j in range(len(assessments[i])):
                    if column_names[j] == 'assessment_schedule_date':
                        assessment_schedule_date = strftime('%d %b %Y', localtime(assessments[i][j]))
                        item[column_names[j]] = assessment_schedule_date
                    else:
                        item[column_names[j]] = assessments[i][j]
                output.append(item)
                item = {}
            return output
        else:
            return None
    except Exception as e:
        logger.error(f"Error fetching assessments in date range: {e}")
        return None


def get_dev_assessments_count(user_id):
    try:
        subquery = db.session.query(ResourceMembers.resource_id).filter(ResourceMembers.resource_member == user_id)
        query = db.session.query(Assessments.assessment_id).filter(
            Assessments.resource_id.in_(subquery)).order_by(desc(Assessments.assessment_schedule_date))
        assessments_count = query.count()
       
        return assessments_count
    except Exception as e:
        logger.error(f"Error fetching total assessments count: {e}")
        return None


def get_dev_recommendations_count(user_id):
    try:
        subquery_2 = db.session.query(ResourceMembers.resource_id).filter(ResourceMembers.resource_member == user_id)
        subquery = db.session.query(Assessments.assessment_id).filter(Assessments.resource_id.in_(subquery_2)).filter(
            Assessments.assessment_status == 3).order_by(
            desc(Assessments.assessment_schedule_date)).first()
        query = db.session.query(AssessmentRecommendations.recommendation_id).filter(
            AssessmentRecommendations.assessment_id.in_(subquery))
        recommendations_count = query.count()
        return recommendations_count
    except Exception as e:
        logger.error(f"Error fetching total recommendations count: {e}")
        return None


def get_dev_recommendations_completed_count(user_id):
    try:
        subquery_2 = db.session.query(ResourceMembers.resource_id).filter(ResourceMembers.resource_member == user_id)
        subquery = db.session.query(Assessments.assessment_id).filter(Assessments.resource_id.in_(subquery_2)).filter(
            Assessments.assessment_status == 3).order_by(
            desc(Assessments.assessment_schedule_date)).first()
        query = db.session.query(AssessmentRecommendations.recommendation_id).filter(
            AssessmentRecommendations.assessment_id.in_(subquery)).filter(
            AssessmentRecommendations.recommendation_status >= 5)
        recommendations_count = query.count()
        return recommendations_count
    except Exception as e:
        logger.error(f"Error fetching total recommendations count: {e}")
        return None


def get_dev_recommendations_completed(user_id):
    try:
        subquery_2 = db.session.query(ResourceMembers.resource_id).filter(ResourceMembers.resource_member == user_id)
        subquery = db.session.query(Assessments.assessment_id).filter(Assessments.resource_id.in_(subquery_2)).order_by(
            desc(Assessments.assessment_schedule_date)).first()
        query = db.session.query(AssessmentRecommendations.recommendation_id).filter(
            AssessmentRecommendations.assessment_id.in_(subquery)).filter(
            AssessmentRecommendations.recommendation_status == 0)
        recommendations_count = query.count()
        return recommendations_count
    except Exception as e:
        logger.error(f"Error fetching recommendations completed count: {e}")
        return None


def get_dev_resource_owner(user_id):
    try:
        subquery_2 = db.session.query(ResourceMembers.resource_id).filter(ResourceMembers.resource_member == user_id)
        subquery = db.session.query(Resources.resource_owner).filter(Resources.resource_id.in_(subquery_2)).first()
        query = db.session.query(Profile.f_name, Profile.l_name).filter(
            Profile.user_id.in_(subquery))
        recommendations_count = query.first()
        return recommendations_count[0] + ' ' + recommendations_count[1]
    except Exception as e:
        logger.error(f"Error fetching resource owner: {e}")
        return None


def get_dev_recommendations_completed_percent(user_id):
    try:
        subquery_2 = db.session.query(ResourceMembers.resource_id).filter(ResourceMembers.resource_member == user_id)
        subquery = db.session.query(Assessments.assessment_id).filter(Assessments.resource_id.in_(subquery_2)).filter(
            Assessments.assessment_status == 3).order_by(
            desc(Assessments.assessment_schedule_date)).first()
        query = db.session.query(AssessmentRecommendations.recommendation_id, AssessmentRecommendations.recommendation_status).filter(
            AssessmentRecommendations.assessment_id.in_(subquery))
        recommendations_total_count = query.count()
        recommendations_completed_count = 0
        recommendations = query.all()
        if recommendations is not None:
            item = {}
            output = []
            column_names = query.statement.columns.keys()
            for i in range(len(recommendations)):
                for j in range(len(recommendations[i])):
                    if column_names[j] == 'recommendation_status':
                        if recommendations[i][j] == 6:
                            recommendations_completed_count = recommendations_completed_count + 1
                    item[column_names[j]] = recommendations[i][j]
                output.append(item)
                item = {}
            recommendations_percent = round((recommendations_completed_count/recommendations_total_count) * 100, 2)
            return recommendations_percent
        else:
            return None
    except Exception as e:
        logger.error(f"Error fetching resource owner: {e}")
        return None




# -----------------------------------Analytics Dashboard----------------------------------------------------

def timestamp_to_mmddyy(epoch):
    return datetime.fromtimestamp(epoch).strftime('%m:%d:%y')

def get_quarterly_assessment_counts(user_id):
    try:
        current_year = datetime.now().year
        previous_year = current_year - 1

        quarterly_counts = []  # List to hold assessment counts for each quarter
        quarterly_dates = []   # List to hold start and end timestamps for each quarter
        
        # Loop through each quarter of the previous year
        for quarter in range(1, 5):
            # Calculate the start and end timestamps of the quarter
            quarter_start = datetime(previous_year, (quarter - 1) * 3 + 1, 1)
            quarter_end = quarter_start + timedelta(days=90)

            # Query to count the assessments within the quarter for the given user_id
            count = db.session.query(func.count(Assessments.assessment_id))\
                .filter(Assessments.assessor_user_id == user_id)\
                .filter(Assessments.assessment_end_date >= quarter_start.timestamp())\
                .filter(Assessments.assessment_end_date <= quarter_end.timestamp())\
                .scalar()

            # Append the count and the start and end timestamps to the respective lists
            quarterly_counts.append(count)
            quarterly_dates.append((timestamp_to_mmddyy(quarter_end.timestamp())))

        dict_count = {}
        # print(quarterly_counts, quarterly_dates)
        for i in range(len(quarterly_dates)):
            dict_count[quarterly_dates[i]] = quarterly_counts[i]
        return dict_count
        # return quarterly_counts, quarterly_dates
    
    except Exception as e:
        logger.error(f"Error fetching quarterly assessment counts: {e}")
        return None, None



def get_analytics_dashboard_service(user_id):
    try:
        # Fetch quarterly assessment counts
        graph_count = get_quarterly_assessment_counts(user_id)

        # Fetch the current assessment score (latest non-null assessment_end_date)
        current_assessment_scores = db.session.query(Assessments.score)\
            .filter(Assessments.assessor_user_id == user_id)\
            .filter(Assessments.assessment_end_date.isnot(None))\
            .order_by(desc(Assessments.assessment_end_date))\
            .limit(1)\
            .scalar()

        # Fetch the previous assessment score (second latest non-null assessment_end_date)
        previous_assessment_scores = db.session.query(Assessments.score)\
            .filter(
                Assessments.assessor_user_id == user_id, 
                Assessments.assessment_end_date.isnot(None),
                Assessments.assessment_end_date < db.session.query(func.max(Assessments.assessment_end_date))
                    .filter(Assessments.assessor_user_id == user_id)
                    .scalar_subquery()
            )\
            .order_by(desc(Assessments.assessment_end_date))\
            .limit(1)\
            .scalar()

        # Fetch the last assessment date (latest completed assessment)
        last_assessment = db.session.query(Assessments.assessment_end_date)\
            .filter(Assessments.assessor_user_id == user_id)\
            .filter(Assessments.assessment_end_date.isnot(None))\
            .order_by(desc(Assessments.assessment_end_date))\
            .limit(1)\
            .scalar()

        # Fetch total number of assessments
        total_assessments = db.session.query(func.count(Assessments.assessment_id))\
            .filter(Assessments.assessor_user_id == user_id)\
            .scalar()

        # Fetch total number of recommendations assigned to the user
        total_recommendations = db.session.query(func.count(AssessmentRecommendations.recommendation_id))\
            .filter(AssessmentRecommendations.assign_to == user_id)\
            .scalar()

        # Fetch total number of completed recommendations
        completed_recommendations = db.session.query(func.count(AssessmentRecommendations.recommendation_id))\
            .filter(
                AssessmentRecommendations.assign_to == user_id, 
                AssessmentRecommendations.recommendation_status == 4
            )\
            .scalar()

        return {
            "current_assessment_score": current_assessment_scores,
            "previous_assessment_score": previous_assessment_scores,
            "last_assessment": last_assessment,
            "total_assessments": total_assessments,
            "total_recommendations": total_recommendations,
            "completed_recommendations": completed_recommendations,
            "bargraph_count": graph_count,
            "total_last_two": sum(list(graph_count.values())[-2:]),
            "total_bargraph_count": sum(list(graph_count.values())),
        }
    except Exception as e:
        logger.error(f"Error fetching resource owner: {e}")
        return None

# -------------------------------------------------------------------------------------------------------------------------------

def get_resource_owner_details_service(user_id):
    try:
        query = db.session.query(ResourceMembers.resource_member, Resources.resource_id, Profile.f_name, Profile.l_name, 
                                 Organizations.org_name, Resources.resource_name, Resources.description).\
                join(Resources, ResourceMembers.resource_id == Resources.resource_id).\
                join(Profile, Resources.resource_owner == Profile.user_id).\
                join(Organizations, Resources.org_id == Organizations.org_id).\
                filter(ResourceMembers.resource_member == user_id)

        resource = query.all()
        item = {}
        column_names = query.statement.columns.keys()
        for i in range(len(resource)):
            for j in range(len(resource[i])):
                item[column_names[j]] = resource[i][j]
        return item
    except Exception as e:
        logger.error(f"Error fetching resource owner: {e}")
        return None
