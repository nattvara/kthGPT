from typing import Optional

from . import client, clean_response
from db.models import Lecture


INDEX_NAME = 'lecture'


def clean():
    client.indices.delete(
        index=INDEX_NAME,
        ignore=[400, 404],
    )


def index(lecture: Lecture):
    client.index(
        index=INDEX_NAME,
        body=lecture.to_doc(),
        id=lecture.id,
        refresh=True,
    )


def wildcard_search_course_code(search_string: str, course_code: str):
    output_fields = [
        'public_id',
        'language',
        'approved',
        'source',
        'date',
        'words',
        'length',
        'title',
        'preview_uri',
        'content_link',
        'courses',
    ]

    query_string = f"*{'*'.join(search_string.split(' '))}*"

    query = {
        'query': {
            'bool': {
                'must': [
                    {
                        'match': {
                            'courses': course_code,
                        }
                    }
                ],
                'filter': {
                    'query_string': {
                        'query': query_string,
                        'fields': [
                            'source',
                            'title',
                        ]
                    }
                }
            }
        },
        'fields': output_fields,
        'sort': {
            'date': {
                'order': 'desc',
            },
        },
    }

    response = client.search(
        index=INDEX_NAME,
        body=query,
    )

    return clean_response(response, output_fields)


def term_query_no_courses():
    output_fields = [
        'public_id',
        'language',
        'approved',
        'source',
        'date',
        'words',
        'length',
        'title',
        'preview_uri',
        'content_link',
    ]

    query = {
        'query': {
            'term': {
                'no_course': True,
            }
        },
        'fields': output_fields,
        'size': 5000,
        'sort': {
            'date': {
                'order': 'desc',
            },
        },
    }

    response = client.search(
        index=INDEX_NAME,
        body=query,
    )

    return clean_response(response, output_fields)


def match_all_count() -> int:
    query = {
        'query': {
            'match_all': {}
        },
        'fields': [],
        'size': 0,
    }

    response = client.search(
        index=INDEX_NAME,
        body=query,
    )

    return response['hits']['total']['value']


def term_query_no_courses_count() -> int:
    query = {
        'query': {
            'term': {
                'no_course': True,
            }
        },
        'fields': [],
        'size': 0,
    }

    response = client.search(
        index=INDEX_NAME,
        body=query,
    )

    return response['hits']['total']['value']
