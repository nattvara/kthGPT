

def test_index_response(api_client):
    response = api_client.get('/')

    assert response.status_code == 200
    assert response.json() == {'message': 'I am the API.'}
