from run import app

def get_test_token():
    with app.test_client() as c:
        response = c.post('/auth/login', json={'username': 'john.doe@impacthub.com', 'password': 'iowasandroid'})
        token = response.json
        return token['access_token']
    
def test_get_billings():
    token = get_test_token()
    with app.test_client() as c:
        response = c.get('/billing/',headers={'Authorization':f'Bearer {token}'})
        assert response.status_code == 200

def test_get_billing():
    token = get_test_token()
    with app.test_client() as c:
        response = c.get('/billing/1',headers={'Authorization':f'Bearer {token}'})
        assert response.status_code == 200

def test_get_org_billings():
    token = get_test_token()
    with app.test_client() as c:
        response = c.get('/billing/org/1',headers={'Authorization':f'Bearer {token}'})
        assert response.status_code == 200

def test_get_billing_by_user_id():
    token = get_test_token()
    with app.test_client() as c:
        response = c.get('/billing/details/1',headers={'Authorization':f'Bearer {token}'})
        assert response.status_code == 200
