import index.lecture as lecture_index


def test_search_performs_bool_query(mocker):
    client = mocker.patch('index.client.search', return_value={
        'hits': {
            'hits': [
                {
                    'fields': {
                        'title': ['Some title']
                    }
                }
            ]
        }
    })

    response = lecture_index.search('Some title', 'XX1337')

    assert response[0]['title'] == 'Some title'

    args = client.mock_calls[0][2]
    assert 'bool' in args['body']['query']
