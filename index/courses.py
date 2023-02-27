from typing import Optional

from . import client, clean_response
from db.models import CourseWrapper


INDEX_NAME = 'course'


def clean():
    client.indices.delete(
        index=INDEX_NAME,
        ignore=[400, 404],
    )


def create():
    index_body = {
        'settings': {
            'analysis': {
                'filter': {
                    'word_delimiter_graph_course': {
                        'type': 'word_delimiter_graph',
                        'preserve_original': True,
                    },
                    'edge_ngram_course': {
                        'type': 'edge_ngram',
                        'min_gram': 1,
                        'max_gram': 6,
                    },
                },
                'analyzer': {
                    'course_analyzer': {
                        'tokenizer': 'keyword',
                        'filter': [
                            'lowercase',
                            'word_delimiter_graph_course',
                            'edge_ngram_course',
                        ],
                    },
                },
            },
        },
        'mappings': {
            'properties': {
                'course_code': {
                    'type': 'text',
                    'analyzer': 'course_analyzer',
                    'search_analyzer': 'standard',
                },
                'swedish_name': {
                    'type': 'search_as_you_type',
                },
                'english_name': {
                    'type': 'search_as_you_type',
                },
                'alternate_course_codes': {
                    'type': 'text',
                    'analyzer': 'course_analyzer',
                    'search_analyzer': 'standard',
                },
                'alternate_english_names': {
                    'type': 'search_as_you_type',
                },
                'alternate_swedish_names': {
                    'type': 'search_as_you_type',
                },
            }
        }
    }
    client.indices.create(
        index=INDEX_NAME,
        body=index_body,
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
    sort_by_lecture_count: Optional[bool] = False,
    apply_filter: Optional[bool] = True,
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
                'should': [
                    {
                        'multi_match': {
                            'query': search_string,
                            'type': 'bool_prefix',
                        },
                    },
                ],
            }
        },
        'fields': output_fields,
        '_source': False,
    }

    if apply_filter:
        query['query']['bool']['filter'] = {
            'multi_match': {
                'query': search_string,
                'type': 'bool_prefix',
                'fields': [
                    'course_code',
                    'swedish_name',
                    'english_name',
                    'alternate_course_codes',
                    'alternate_english_names',
                    'alternate_swedish_names',
                ]
            },
        }

    for word in search_string.split(' '):
        query['query']['bool']['should'].append({
            'multi_match': {
                'type': 'bool_prefix',
                'query': word,
                'fields': [
                    'course_code',
                    'alternate_course_codes',
                ],
                'boost': 15,
            },
        })

    if unlimited:
        query['size'] = 5000  # not actually unlimited
    else:
        query['size'] = limit

    if sort_by_lecture_count:
        query['sort'] = {
            'lectures': {
                'order': 'desc',
            }
        }

    response = client.search(
        index=INDEX_NAME,
        body=query,
    )

    return clean_response(response, output_fields)


def at_least_one_lecture_count() -> int:
    query = {
        'query': {
            'range': {
                'lectures': {
                    'gte': 1,
                },
            }
        },
        'size': 0,
    }

    response = client.search(
        index=INDEX_NAME,
        body=query,
    )

    return response['hits']['total']['value']
