import flask
from flask import Blueprint, jsonify, request
from app.activities.routes import get_my_activities
from app.user.services import get_profile
import os
from flask_cors import cross_origin, CORS
from flask_jwt_extended import jwt_required
from .services import *
from app.log_handler import get_logger
from app import cache
from flasgger import swag_from
from app.user.services import switch_community_service
logger = get_logger()

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
CORS(bp)
def make_cache_key(*args, **kwargs):
   return f"dashboard_{request.view_args}"

def get_swagger_file(module_name, yaml_filename):
    module_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(module_dir, 'docs')
    return os.path.join(docs_dir, yaml_filename)


'''
    Get resource owner dashboard
'''

# Supplementary dashboard
@bp.route("/rodetails/<int:user_id>/<practice_area>", methods=['GET'])
@swag_from(get_swagger_file('dashboard', 'ro_dashboard_stats.yml'))
@cache.cached(timeout=50, key_prefix=make_cache_key)
# @cross_origin()
def dashboard_stats(user_id, practice_area):
    '''Required Imports For this service'''
    from app.resources.services import get_current_badge_service_for_latest_assessment
    from app.recommendations.services import fetch_kpi_and_goals_for_latest_assessment

    ''' Main Code '''
    response,status = get_subscribed_communities(user_id)
    resource = db.session.query(Resources).filter(Resources.resource_owner==user_id).first()
    resource_id = resource.resource_id
    if response:
        communities = response.json()
        communities_list = [community for community in communities if community['practice_area'].lower()==practice_area.lower()]
        if communities_list:
            community_details = {"name":practice_area,"communities":communities_list}
    user_profile = get_user_profile(practice_area)
    current_score = get_current_score_service(user_id,practice_area,resource_id)
    # highest_score = get_highest_maturity_score_by_practice_area(practice_area)
    # lowest_score = get_lowest_maturity_score_by_practice_area(practice_area)
    # recommendations_count = get_recommendations_count()
    # maturity_score_overview = get_quarterly_maturity_scores(practice_area)
    peer_comparison = get_peer_comparison(user_id,practice_area)
    # historical_timeline = get_quarterly_assessments(practice_area)
    benchmark = get_benchmarking_comparison(practice_area)
    # area_scores = get_knowledge_area_scores(practice_area)
    strategic_recom = get_recommendations_by_user(practice_area,resource_id)
    badge,milestone = get_current_badge_service_for_latest_assessment(user_id,practice_area)
    maturity_progression = get_maturity_assessment_progression(resource_id,practice_area)
    kpi_and_goals = fetch_kpi_and_goals_for_latest_assessment(user_id)

    kpi_data = []
    for kpi in kpi_and_goals["kpi"]:
        knowledge_area = kpi["knowledge_area"]
        progress = kpi["kpi_goal"]["goal"]["progress_percentage"]
        description = kpi["kpi_goal"]["goal"]["description"]
        
        kpi_data.append({
            "name": knowledge_area,
            "progress": progress,
            "description": description
        })

    output = {
        'current_score':current_score,
        'user_profile':user_profile,
        'peer_comparison': peer_comparison,
        'benchmark': benchmark,
        'engaged_community_areas':community_details if community_details else None,
        'subscribed_communities':communities if communities else None,
        'strategic_recom':strategic_recom,
        'badge':badge,
        'badge_milestone':milestone,
        'maturity_progression':maturity_progression,
        'kpi_and_goals':{'last_assessment':current_score['assessment_taken'],'kpi_data':kpi_data}
        }
    
    if output is not None:
        return (output), 200
    else:
        return jsonify(), 200


@bp.route("/ro/daterange/<int:start_date>/<int:end_date>", methods=['GET'])
@cross_origin()
def dashboard_daterange(start_date, end_date):
    assessments = get_daterange_assessments(start_date, end_date)
    if assessments is not None:
        return jsonify(assessments), 200
    else:
        return jsonify(), 200


# search by community name or practice area
@bp.route("/ro/search/<keyword>", methods=['GET'])
@swag_from(get_swagger_file('dashboard', 'search_comm_by_keyword.yml'))
@cross_origin()
def search(keyword):
    result, status_code = search_community_practice_area(keyword)
    if status_code != 200:
        return jsonify(message=result),  404
    return jsonify(result.json()),    200

# get number of subscriber for each community
@bp.route("/ro/subscribers", methods=['GET'])
@swag_from(get_swagger_file('dashboard', 'subscribers_for_community.yml'))
@cross_origin()
def get_Subscribers_count():
    result, status_code = get_communities_subscriber()
    if status_code != 200:
        return jsonify(message=result),  404
    return jsonify(result),    200

# get maturity score 
@bp.route("/ro/maturityscore", methods=['GET'])
@swag_from(get_swagger_file('dashboard', 'maturity_score.yml'))
@cross_origin()
def get_maturity_score_for_resource():
    result, status_code = get_maturity_score()
    if status_code != 200:
        return jsonify(message=result),  404
    return jsonify(result),    200


@bp.route("/ro/maturityscore/<int:community_id>", methods=['GET'])
@cross_origin()
def get_maturity_score_by_community(community_id):
    result, status_code = get_maturity_score_by_community_id(community_id)
    if status_code != 200:
        return jsonify(message=result),  404
    return jsonify(result), 200

# get subscribed communities
@bp.route("/ro/getcommunities/<user_id>", methods=['GET'])
@cache.cached(timeout=50, key_prefix=make_cache_key)
@swag_from(get_swagger_file('dashboard', 'community_by_user_id.yml'))
# @cross_origin()
def get_subscribed_communities_resourceid(user_id):
    result, status_code = get_subscribed_communities(user_id)
    if status_code != 200:
        return jsonify(message=result),  404
    return jsonify(result.json()),    200

# get community by id
@bp.route("/ro/community/<int:community_id>", methods=['GET'])
@cross_origin()
def get_community_by_id_route(community_id):
    result, status_code = get_community_by_id_service(community_id)
    if status_code != 200:
        return jsonify(message=result),  404
    return jsonify(result.json()),    200

# create community subscription
@bp.route('/subscribe', methods=['POST'])
# @jwt_required()
def create_community_subscription_routes():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    data = request.get_json()
    result, status_code = create_community_subscription_service(data)
    if status_code != 200:
        return jsonify(message=result), 404
    return jsonify(result), 200


@bp.route('/unsubscribe/<int:user_id>/<int:community_id>', methods=['DELETE'])
def delete_community_subscription_route(user_id, community_id):
    result, status_code = delete_community_subscription_service(user_id, community_id)
    if status_code != 200:
        return jsonify(message=result), 404
    return jsonify(result), 200


# get billing by user_id
@bp.route("/ro/billing", methods=['POST'])
@cross_origin()
def get_billing():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    data = request.get_json()
    tempbill, status_code= get_billing_service(data)
    if status_code != 200:
        return jsonify(message=tempbill),  404
    return jsonify(tempbill.json()),    200

#get current score for different projects by practice_area
@bp.route("/ro/score/<practice_area>", methods=['GET'])
@cross_origin()
def get_current_score_based_on_practice_area(practice_area):
    score_data = get_current_score_service(practice_area)
    return score_data,200

@bp.route("/ro/highestscore/<practice_area>", methods=['GET'])
@cross_origin()
def get_highest_maturity_score_by_practice_area_route(practice_area):
    try:
        result, status_code =  get_highest_maturity_score_by_practice_area(practice_area)
       
        if status_code != 200:
            return jsonify(message=result), 404
       
        return jsonify(result), 200
   
    except Exception as e:
        # Log any unexpected exceptions
        logger.error(f"Error: {e}")
        return jsonify(message="Internal Server Error"), 500

@bp.route("/ro/lowestscore/<practice_area>", methods=['GET'])
@cross_origin()
def get_lowest_maturity_score_by_practice_area_route(practice_area):
    try:
        result, status_code = get_lowest_maturity_score_by_practice_area(practice_area)
       
        if status_code != 200:
            return jsonify(message=result), 404
       
        return jsonify(result), 200
   
    except Exception as e:
        # Log any unexpected exceptions
        logger.error(f"Error: {e}")
        return jsonify(message="Internal Server Error"), 500
    
######################################
# Developer Dashboard
######################################


@bp.route("/dev/<int:user_id>", methods=['GET'])
@cross_origin()
def dev_dashboard_stats(user_id):
    user_profile = get_dev_uname(user_id)
    score_matrix = get_dev_score_cur_prev(user_id)
    assessments_count = get_dev_assessments_count(user_id)
    recommendations_count = get_dev_recommendations_count(user_id)
    recommendations_completed_count = get_dev_recommendations_completed_count(user_id)
    resource_owner = get_dev_resource_owner(user_id)
    recommendations_percentage = get_dev_recommendations_completed_percent(user_id)

    output = {'user_profile': user_profile, 'score_matrix': score_matrix, 'assessments_count': assessments_count,
              'resource_owner': resource_owner, 'total_recommendations': recommendations_count, 'recommendations_completed_count': recommendations_completed_count, 'recommendations_percentage': recommendations_percentage}
    if output is not None:
        return jsonify(output), 200
    else:
        return jsonify(), 200
    

# -----------------------------------Analytics Dashboard----------------------------------------------------

@bp.route('/get/<int:user_id>', methods=['GET'])
def dashboard_route(user_id):
    dashboard_data = get_analytics_dashboard_service(user_id)
    if not dashboard_data:
        return jsonify({'msg': 'No data found for the dashboard'}), 404
    else:
        return jsonify(dashboard_data), 200
    

@bp.route('/get/owner/<int:user_id>', methods=['GET'])
def dashboard_owner_route(user_id):
    dashboard_data = get_resource_owner_details_service(user_id)
    if not dashboard_data:
        return jsonify({'msg': 'No data found for the dashboard'}), 404
    else:
        return jsonify(dashboard_data), 200
    

# ----------------------------------------------------------------------------------------------------------
@bp.route('/switch/community/<user_id>',methods=['PUT'])
def switch_community_area_service(user_id):
    data = request.get_json()
    if not data:
        return jsonify(f"missing json in request"),400
    result,status = switch_community_service(user_id,data)
    if not result:
        return jsonify({'msg': 'Failed to switch community'}), 500
    
    return jsonify(result),200