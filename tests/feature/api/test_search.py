from unittest.mock import call
from io import BytesIO
from PIL import Image
import filecmp
import random

from db.models import Lecture
import api.routers.search
from db.crud import (
    get_image_upload_by_public_id,
)


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
        apply_filter=True,
        source=None,
        group=None,
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
        apply_filter=True,
        source=None,
        group=None,
    )


def test_lecture_search_inside_course_can_be_restricted_to_source(mocker, api_client, analysed_lecture):
    doc = analysed_lecture.to_doc()
    doc['date'] = doc['date'].isoformat()
    index = mocker.patch('index.lecture.search_in_course', return_value=[
        doc,
        doc,
    ])

    response = api_client.post('/search/course/XX1337', json={
        'query': 'some query',
        'source': 'youtube',
    })

    assert len(response.json()) == 2
    assert index.call_count == 1
    assert index.mock_calls[0] == call(
        'some query',
        'XX1337',
        apply_filter=True,
        source='youtube',
        group=None,
    )


def test_lecture_search_inside_course_includes_kth_raw_with_kth_source(mocker, api_client, analysed_lecture):
    doc = analysed_lecture.to_doc()
    doc['date'] = doc['date'].isoformat()
    index = mocker.patch('index.lecture.search_in_course', return_value=[
        doc,
        doc,
    ])

    response = api_client.post('/search/course/XX1337', json={
        'query': 'some query',
        'source': 'kth',
    })

    assert len(response.json()) == 4
    assert index.call_count == 2
    assert index.mock_calls[0] == call(
        'some query',
        'XX1337',
        apply_filter=True,
        source='kth',
        group=None,
    )
    assert index.mock_calls[1] == call(
        'some query',
        'XX1337',
        apply_filter=True,
        source='kth_raw',
        group=None,
    )


def test_lecture_search_inside_course_can_be_restricted_to_group(mocker, api_client, analysed_lecture):
    doc = analysed_lecture.to_doc()
    doc['date'] = doc['date'].isoformat()
    index = mocker.patch('index.lecture.search_in_course', return_value=[
        doc,
        doc,
    ])

    response = api_client.post('/search/course/XX1337', json={
        'query': 'some query',
        'group': 'some_group',
    })

    assert len(response.json()) == 2
    assert index.call_count == 1
    assert index.mock_calls[0] == call(
        'some query',
        'XX1337',
        apply_filter=True,
        source=None,
        group='some_group',
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
    assert index.call_count == 1
    assert response.json()[0]['highlight']['transcript'][0] == '00:00 -> 00:30 foo'


def test_image_search_creates_image_upload(mocker, api_client, img_file):
    mocker.patch('jobs.schedule_image_search')

    response = api_client.post(
        '/search/image',
        files={
            'file': ('a_file_name.png', open(img_file, 'rb'), 'image/png')
        }
    )

    image_id = response.json()['id']

    upload = get_image_upload_by_public_id(image_id)

    assert upload is not None


def test_image_search_will_not_save_the_same_image_twice(mocker, api_client, img_file):
    mocker.patch('jobs.schedule_image_search')

    def func():
        response = api_client.post(
            '/search/image',
            files={
                'file': ('a_file_name.png', open(img_file, 'rb'), 'image/png')
            }
        )
        return response

    response = func()
    image_id_1 = response.json()['id']

    response = func()
    image_id_2 = response.json()['id']

    assert image_id_1 == image_id_2


def test_image_search_saves_png_file_upload(mocker, api_client, img_file):
    mocker.patch('jobs.schedule_image_search')

    response = api_client.post(
        '/search/image',
        files={
            'file': ('a_file_name.png', open(img_file, 'rb'), 'image/png')
        }
    )

    image_id = response.json()['id']

    upload = get_image_upload_by_public_id(image_id)
    assert filecmp.cmp(img_file, upload.get_filename())


def test_image_search_can_retrieve_image(api_client, image_upload):
    response = api_client.get(f'/search/image/{image_upload.public_id}/img')

    image = Image.open(BytesIO(response.content))
    assert image.format == 'PNG'


def test_image_search_can_retrieve_info(api_client, image_upload):
    image_upload.text_content = 'foo'
    image_upload.description_en = 'bar'
    image_upload.description_sv = 'baz'
    image_upload.save()

    response = api_client.get(f'/search/image/{image_upload.public_id}')

    assert response.json()['text_content'] == 'foo'
    assert response.json()['description_en'] == 'bar'
    assert response.json()['description_sv'] == 'baz'


def test_image_upload_schedules_image_search_pipeline(mocker, api_client, img_file):
    schedule_image_search_mock = mocker.patch('jobs.schedule_image_search')

    response = api_client.post(
        '/search/image',
        files={
            'file': ('a_file_name.png', open(img_file, 'rb'), 'image/png')
        }
    )

    image_id = response.json()['id']
    image = get_image_upload_by_public_id(image_id)

    assert schedule_image_search_mock.call_count == 1
    assert schedule_image_search_mock.mock_calls[0] == call(image)


def test_image_question_can_be_created_for_uploaded_image(mocker, api_client, image_upload):
    mocker.patch('tools.text.ai.gpt3', return_value='')
    mocker.patch('index.lecture.search_in_transcripts_and_titles')

    assert len(image_upload.questions()) == 0

    api_client.post(
        f'/search/image/{image_upload.public_id}/questions',
        json={
            'query': 'help me',
        }
    )

    assert len(image_upload.questions()) == 1
    assert image_upload.questions()[0].query_string == 'help me'


def test_image_question_runs_searches_for_each_query(mocker, api_client, image_upload):
    mocker.patch('tools.text.ai.gpt3', return_value='')
    index_mock = mocker.patch('index.lecture.search_in_transcripts_and_titles')

    swedish_queries = len(image_upload.get_search_queries_sv())
    english_queries = len(image_upload.get_search_queries_en())

    api_client.post(
        f'/search/image/{image_upload.public_id}/questions',
        json={
            'query': 'help me',
        }
    )

    assert index_mock.call_count == swedish_queries + english_queries


def test_image_question_aggregates_the_top_hits(mocker, api_client, image_upload):
    mocker.patch('tools.text.ai.gpt3', return_value='')

    lecture1 = Lecture(
        public_id='id-1',
        language='sv',
        approved=True,
        title='A lecture',
    )
    lecture1.save()
    lecture2 = Lecture(
        public_id='id-2',
        language='sv',
        approved=True,
        title='A lecture',
    )
    lecture2.save()

    # Override the limit to match the sample below,
    # with the given sample below, we only care about two docs (matching the created lectures)
    api.routers.search.MAX_NUMBER_IMAGE_HITS = 2

    # Create two sample of hits
    # The documents at index 3 and 6 have way higher scores
    # This test should prove that these two gets returned
    sample_1 = [
        {
            '_id': 100,
            '_score': 1.1,
        },
        {
            '_id': 101,
            '_score': 1.17,
        },
        {
            '_id': lecture1.id,
            '_score': 5.51,
        },
        {
            '_id': 102,
            '_score': 1.4,
        },
        {
            '_id': 103,
            '_score': 2.23,
        },
        {
            '_id': lecture2.id,
            '_score': 1.1253,
        },
        {
            '_id': 104,
            '_score': 1.3344,
        },
    ]
    sample_2 = [
        {
            '_id': 100,
            '_score': 3.42341,
        },
        {
            '_id': 101,
            '_score': 1.17342,
        },
        {
            '_id': lecture1.id,
            '_score': 7.92344,
        },
        {
            '_id': 102,
            '_score': 2.544,
        },
        {
            '_id': 103,
            '_score': 0.73234,
        },
        {
            '_id': lecture2.id,
            '_score': 5.177423,
        },
        {
            '_id': 104,
            '_score': 0.1,
        },
    ]

    def random_sample(query: str, include_id=False, include_score=False):
        random_number = random.randint(0, 1)
        if random_number == 0:
            return sample_1
        return sample_2

    index_mock = mocker.patch('index.lecture.search_in_transcripts_and_titles', side_effect=random_sample)

    swedish_queries = len(image_upload.get_search_queries_sv())
    english_queries = len(image_upload.get_search_queries_en())

    response = api_client.post(
        f'/search/image/{image_upload.public_id}/questions',
        json={
            'query': 'help me',
        }
    )

    assert index_mock.call_count == swedish_queries + english_queries
    assert len(response.json()['hits']) == 2
    for lecture in response.json()['hits']:
        assert lecture['public_id'] in ['id-1', 'id-2']


def test_answer_to_question_hit_can_be_retrieved(
    mocker,
    api_client,
    image_upload,
    analysed_lecture,
):
    mocker.patch('index.lecture.search_in_transcripts_and_titles', return_value=[
        {
            '_id': analysed_lecture.id,
            '_score': 3.14,
        }
    ])
    mocker.patch('tools.text.ai.gpt3', return_value='you can find the answer here')

    response = api_client.post(
        f'/search/image/{image_upload.public_id}/questions',
        json={
            'query': 'help me',
        }
    )

    question_id = response.json()['id']
    hit = response.json()['hits'][0]

    response = api_client.get(
        f'/search/image/{image_upload.public_id}/questions/{question_id}/{hit["public_id"]}/{hit["language"]}/answer',
    )

    assert response.json()['answer'] == 'you can find the answer here'


def test_relevance_of_hit_can_be_retrieved(
    mocker,
    api_client,
    image_upload,
    analysed_lecture,
):
    mocker.patch('index.lecture.search_in_transcripts_and_titles', return_value=[
        {
            '_id': analysed_lecture.id,
            '_score': 3.14,
        }
    ])
    mocker.patch('tools.text.ai.gpt3', return_value='this is relevant because')

    response = api_client.post(
        f'/search/image/{image_upload.public_id}/questions',
        json={
            'query': 'help me',
        }
    )

    question_id = response.json()['id']
    hit = response.json()['hits'][0]

    response = api_client.get(
        f'/search/image/{image_upload.public_id}/questions/{question_id}/{hit["public_id"]}/{hit["language"]}/relevance',
    )

    assert response.json()['relevance'] == 'this is relevant because'
