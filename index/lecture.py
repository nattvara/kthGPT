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
        'words',
        'length',
        'title',
        'preview_uri',
        'content_link',
        'courses',
    ]

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
                        'query': f'{search_string}*'
                    }
                }
            }
        },
        'fields': output_fields,
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
    }

    response = client.search(
        index=INDEX_NAME,
        body=query,
    )

    return clean_response(response, output_fields)
