

def test_read_main(api_client):
    response = api_client.get('/')

    assert response.status_code == 200
    assert response.json() == {'message': 'I am the API.'}
