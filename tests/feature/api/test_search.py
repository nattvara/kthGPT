from unittest.mock import call


def test_api_can_search_courses(mocker, api_client):
    index = mocker.patch('index.courses.wildcard_search', return_value=[
        {
            'course_code': 'XX1337',
            'display_name': 'Course name',
            'lectures': None
        }
    ])

    response = api_client.post('/search/course', json={
        'query': 'XX1337',
        'limit': 40,
    })

    assert response.json()[0]['course_code'] == 'XX1337'
    assert index.call_count == 1
    assert index.mock_calls[0] == call(
        'XX1337',
        include_lectures=None,  # should not include lecture count
        lecture_count_above_or_equal=0,  # include all lectures
        unlimited=False,
        sort_by_lecture_count=False,
        apply_filter=True
    )


def test_limit_must_be_specified(api_client):
    response = api_client.post('/search/course', json={
        'query': 'XX1337',
    })

    assert response.status_code == 400
    assert response.json()['detail'] == 'Please specify a limit to the search result'


def test_course_search_can_include_lecture_count(mocker, api_client):
    index = mocker.patch('index.courses.wildcard_search', return_value=[
        {
            'course_code': 'XX1337',
            'display_name': 'Course name',
            'lectures': 123
        }
    ])

    response = api_client.post('/search/course?include_lectures=true', json={
        'query': 'XX1337',
        'limit': 40,
    })

    assert response.json()[0]['lectures'] == 123
    assert index.call_count == 1
    assert index.mock_calls[0] == call(
        'XX1337',
        include_lectures=True,
        lecture_count_above_or_equal=0,
        unlimited=False,
        sort_by_lecture_count=False,
        apply_filter=True
    )


def test_result_can_be_limited_to_non_courses_with_given_lecture_count(mocker, api_client):
    index = mocker.patch('index.courses.wildcard_search', return_value=[
        {
            'course_code': 'XX1337',
            'display_name': 'Course name',
            'lectures': 123
        }
    ])

    api_client.post('/search/course?lecture_count_above_or_equal=100', json={
        'query': 'XX1337',
        'limit': 40,
    })

    assert index.call_count == 1
    assert index.mock_calls[0] == call(
        'XX1337',
        include_lectures=None,
        lecture_count_above_or_equal=100,
        unlimited=True,
        sort_by_lecture_count=True,
        apply_filter=True
    )


def test_lecture_search_inside_course(mocker, api_client, analysed_lecture):
    doc = analysed_lecture.to_doc()
    doc['date'] = doc['date'].isoformat()
    index = mocker.patch('index.lecture.search_in_course', return_value=[
        doc,
        doc,
    ])

    response = api_client.post('/search/course/XX1337', json={
        'query': 'some query',
    })

    assert len(response.json()) == 2
    assert index.call_count == 1
    assert index.mock_calls[0] == call(
        'some query',
        'XX1337',
        True,
    )


def test_lecture_search_inside_no_course(mocker, api_client, analysed_lecture):
    doc = analysed_lecture.to_doc()
    doc['date'] = doc['date'].isoformat()
    index = mocker.patch('index.lecture.search_in_course', return_value=[
        doc,
    ])

    response = api_client.post('/search/course/no_course', json={
        'query': 'some query',
    })

    assert len(response.json()) == 1
    assert index.call_count == 1
    assert index.mock_calls[0] == call(
        'some query',
        no_course=True,
        apply_filter=True
    )


def test_lecture_transcript_search(mocker, api_client, analysed_lecture):
    doc = analysed_lecture.to_doc()
    doc['date'] = doc['date'].isoformat()
    doc['highlight'] = {
        'transcript': [
            '00:00 -> 00:30 foo',
            '01:00 -> 01:20 <strong>match</strong>',
        ],
        'title': ['<strong>match</strong>'],
    }

    index = mocker.patch('index.lecture.search_in_transcripts_and_titles', return_value=[
        doc,
    ])

    response = api_client.post('/search/lecture', json={
        'query': 'some query',
    })

    assert len(response.json()) == 1
    assert response.json()[0]['highlight']['transcript'][0] == '00:00 -> 00:30 foo'
