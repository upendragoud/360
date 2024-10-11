from run import app

def get_test_token():
    with app.test_client() as c:
        response = c.post('/auth/login',json={'username': 'john.doe@impacthub.com', 'password': 'iowasandroid'})
        return response.json['access_token']
    
def test_get_tasks():
    token = get_test_token()
    with app.test_client() as c:
        response=c.get('/consultants/', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200