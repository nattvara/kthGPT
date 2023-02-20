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


def wildcard_search(search_string: str):
    output_fields = [
        'course_code',
        'display_name',
    ]

    query = {
        'query': {
            'query_string': {
                'query': f'{search_string}*',
                'fields': [
                    'course_code',
                    'swedish_name',
                    'english_name',
                    'alternate_course_codes',
                    'alternate_english_names',
                    'alternate_swedish_names',
                ]
            }
        },
        'fields': output_fields,
        '_source': False,
    }

    response = client.search(
        index=INDEX_NAME,
        body=query,
    )

    return clean_response(response, output_fields)
