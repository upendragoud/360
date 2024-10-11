from run import app
import time

# def get_test_token():
#     with app.test_client() as c:
#         response = c.post('/auth/login', json={'username': 'john.doe@impacthub.com', 'password': 'iowasandroid'})
#         token = response.json
#         return token['access_token']
def get_test_token():
    with app.test_client() as c:
        response = c.post('/auth/login', json={'username': 'john.doe@impacthub.com', 'password': 'iowasandroid'})
        if response.status_code == 200:
            token = response.json.get('access_token')
            if not token:
                raise ValueError("Access token not found in response")
            return token
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 5))  # Default to retry after 5 seconds
            print(f"Rate limited. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            return get_test_token()  # Retry the request after waiting
        else:
            raise Exception(f"Failed to retrieve token. Status code: {response.status_code}")
    
def test_dashboard_stats():
    token = get_test_token()
    with app.test_client() as c:
        response = c.get('/dashboard/ro',headers={'Authorization':f'Bearer {token}'})
        assert response.status_code == 200

def test_dashboard_daterange():
    token = get_test_token()
    with app.test_client() as c:
        response = c.get('/dashboard/ro/daterange/1717331287/1718368087',headers={'Authorization':f'Bearer {token}'})
        assert response.status_code == 200

# def test_dashboard_activities():
#     token = get_test_token()
#     with app.test_client() as c:
#         response = c.get('/dashboard/ro/activities/1',headers={'Authorization':f'Bearer {token}'})
#         assert response.status_code == 200

def test_search():
    token = get_test_token()
    with app.test_client() as c:
        response = c.get('/dashboard/ro/search/python',headers={'Authorization':f'Bearer {token}'})
        assert response.status_code == 200

def test_get_subscribers_count():
    token = get_test_token()
    with app.test_client() as c:
        response = c.get('/dashboard/ro/subscribers',headers={'Authorization':f'Bearer {token}'})
        assert response.status_code == 200

def test_get_maturity_score_for_resource():
    token = get_test_token()
    with app.test_client() as c:
        response=c.get('/dashboard/ro/maturityscore',headers={'Authorization':f'Bearer {token}'})
        assert response.status_code ==200

def test_get_maturity_score_for_resource_No_token():
    token = get_test_token()
    with app.test_client() as c:
        response=c.get('/dashboard/ro/maturityscore')
        assert response.status_code ==401

# ==============need to review==============
# def test_get_maturity_score_by_community():
#     token = get_test_token()
#     with app.test_client() as c:
#         response=c.get('/dashboard/ro/maturityscore/4',headers={'Authorization':f'Bearer {token}'})
#         assert response.status_code == 200

def test_get_subscribed_communities_resourceid():
    token = get_test_token()
    with app.test_client() as c:
        response=c.get('/dashboard/ro/getcommunities/1',headers={'Authorization':f'Bearer {token}'})
        assert response.status_code == 200

# ==============need to review==============
# def test_get_community_by_id_route():
#     token=get_test_token()
#     with app.test_client() as c:
#         response=c.get('/dashboard/ro/community/3',headers={'Authorization':f'Bearer {token}'})
#         assert response.status_code == 200

# ==============need to review==============
# def test_get_billing():
#     token = get_test_token()  
#     user_id = "1"  
#     with app.test_client() as c:
#         response = c.post('/dashboard/ro/billing', 
#                           json={"user_id": user_id},  # Sending user_id in JSON format
#                           headers={'Authorization': f'Bearer {token}'})
#         assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"


def test_get_current_score_for_different_resources_based_on_practice_area():
    token = get_test_token()
    with app.test_client() as c:
        response=c.get('/dashboard/ro/score/python',headers={'Authorization':f'Bearer {token}'})
        assert response.status_code == 200

def test_get_highest_maturity_score_by_practice_area_route():
    token = get_test_token()
    with app.test_client() as c:
        response=c.get('/dashboard/ro/highestscore/SRE',headers={'Authorization':f'Bearer {token}'})
        assert response.status_code == 200

def test_get_lowest_maturity_score_by_practice_area_route():
    token = get_test_token()
    with app.test_client() as c:
        response=c.get('/dashboard/ro/lowestscore/SRE',headers={'Authorization':f'Bearer {token}'})
        assert response.status_code == 200

def test_dev_dashboard_stats():
    token = get_test_token()
    with app.test_client() as c:
        response=c.get('/dashboard/dev/4',headers={'Authorization':f'Bearer {token}'})
        print(response.data)
        assert response.status_code == 200

def test_get_dashboard_route():
    token = get_test_token()
    with app.test_client() as c:
        response=c.get('/dashboard/get/4',headers={'Authorization':f'Bearer {token}'})
        assert response.status_code == 200

def test_get_dashboard_owner_route():
    token = get_test_token()
    with app.test_client() as c:
        response=c.get('/dashboard/get/owner/1',headers={'Authorization':f'Bearer {token}'})
        assert response.status_code == 200
