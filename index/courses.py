from typing import Optional

from . import client, clean_response
from db.models import CourseWrapper


INDEX_NAME = 'course'


def clean():
    client.indices.delete(
        index=INDEX_NAME,
        ignore=[400, 404],
    )


def index(course: CourseWrapper):
    client.index(
        index=INDEX_NAME,
        body=course.to_doc(),
        id=course.course_code,
        refresh=True,
    )


def wildcard_search(
    search_string: str,
    limit: Optional[int] = None,
    include_lectures: Optional[bool] = False,
    lecture_count_above_or_equal: Optional[int] = 0,
    unlimited: Optional[bool] = False,
):
    if limit is None:
        limit = 10

    output_fields = [
        'course_code',
        'display_name',
    ]

    if include_lectures:
        output_fields.append('lectures')

    query = {
        'query': {
            'bool': {
                'must': [
                    {
                        'range': {
                            'lectures': {
                                'gte': lecture_count_above_or_equal,
                            },
                        }
                    }
                ],
                'filter': {
                    'query_string': {
                        'query': f'{search_string}*',
                        'fields': [
                            'course_code',
                            'swedish_name',
                            'english_name',
                            'alternate_course_codes',
                            'alternate_english_names',
                            'alternate_swedish_names',
                        ],
                    }
                }
            }
        },
        'fields': output_fields,
        '_source': False,
    }

    if unlimited:
        query['size'] = 1337  # not actually unlimited
    else:
        query['size'] = limit

    response = client.search(
        index=INDEX_NAME,
        body=query,
    )

    return clean_response(response, output_fields)
