

def test_query_can_be_made_about_lecture(mocker, api_client, analysed_lecture):
    mocker.patch('tools.text.ai.gpt3', return_value='gpt-3 response')

    response = api_client.post('/query', json={
        'lecture_id': analysed_lecture.public_id,
        'language': analysed_lecture.language,
        'query_string': 'some interesting question',
    })

    assert response.json()['response'] == 'gpt-3 response'


def test_query_response_is_cached(mocker, api_client, analysed_lecture):
    gpt3 = mocker.patch('tools.text.ai.gpt3', return_value='gpt-3 response')

    def request():
        return api_client.post('/query', json={
            'lecture_id': analysed_lecture.public_id,
            'language': analysed_lecture.language,
            'query_string': 'some interesting question',
        })

    response = request()
    response = request()

    assert response.json()['response'] == 'gpt-3 response'
    assert gpt3.call_count == 1


def test_query_response_cache_can_be_overridden(mocker, api_client, analysed_lecture):
    gpt3 = mocker.patch('tools.text.ai.gpt3', return_value='gpt-3 response')

    def request():
        return api_client.post('/query', json={
            'lecture_id': analysed_lecture.public_id,
            'language': analysed_lecture.language,
            'query_string': 'some interesting question',
            'override_cache': True,
        })

    response = request()
    response = request()

    assert response.json()['response'] == 'gpt-3 response'
    assert gpt3.call_count == 2
