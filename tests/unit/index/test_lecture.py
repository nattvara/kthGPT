import index.lecture as lecture_index


def test_search_in_course_performs_bool_query(mocker):
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

    response = lecture_index.search_in_course('Some title', 'XX1337')

    assert response[0]['title'] == 'Some title'

    args = client.mock_calls[0][2]
    assert 'bool' in args['body']['query']


def test_search_in_transcript_returns_highlighted_matches(mocker):
    client = mocker.patch('index.client.search', return_value={
        'hits': {
            'hits': [
                {
                    'highlight': {
                        'transcript': [
                            '00:00 -> 00:30 foo',
                            '01:00 -> 01:20 <strong>match</strong>',
                        ]
                    },
                    'fields': {
                        'title': ['Some title']
                    }
                }
            ]
        }
    })

    response = lecture_index.search_in_transcripts_and_titles('Some query string')

    assert response[0]['title'] == 'Some title'
    assert response[0]['highlight']['transcript'][0] == '00:00 -> 00:30 foo'

    args = client.mock_calls[0][2]
    assert 'highlight' in args['body']
