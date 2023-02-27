from typing import Optional

from . import client, clean_response
from db.models import Lecture


INDEX_NAME = 'lecture'


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
                'char_filter': {
                    'underscore_replacement': {
                        'type': 'mapping',
                        'mappings': [
                            '_ => ',
                        ],
                    },
                },
                'analyzer': {
                    'course_code_analyzer': {
                        'tokenizer': 'keyword',
                        'filter': [
                            'lowercase',
                            'word_delimiter_graph_course',
                            'edge_ngram_course',
                        ],
                    },
                    'title_analyzer': {
                        'tokenizer': 'standard',
                        'char_filter': [
                            'underscore_replacement',
                        ],
                        'filter': [
                            'word_delimiter_graph',
                            'lowercase',
                        ],
                    },
                },
            },
        },
        'mappings': {
            'properties': {
                'title': {
                    'type': 'text',
                    'analyzer': 'title_analyzer',
                    'fields': {
                        'standard': {
                            'type': 'search_as_you_type',
                        }
                    },
                },
                'courses': {
                    'type': 'text',
                    'analyzer': 'course_code_analyzer',
                    'search_analyzer': 'standard',
                },
            }
        }
    }
    client.indices.create(
        index=INDEX_NAME,
        body=index_body,
        ignore=[400, 404],
    )


def index(lecture: Lecture):
    client.index(
        index=INDEX_NAME,
        body=lecture.to_doc(),
        id=lecture.id,
        refresh=True,
    )


def search(
    search_string: str,
    course_code: Optional[str] = None,
    apply_filter: Optional[bool] = True,
    no_course: Optional[bool] = False,
):
    output_fields = [
        'public_id',
        'language',
        'approved',
        'source',
        'date',
        'words',
        'length',
        'title',
        'title.standard',
        'preview_uri',
        'preview_small_uri',
        'content_link',
        'courses',
    ]

    query = {
        'query': {
            'bool': {
                'must': [],
                'should': [
                    {
                        'multi_match': {
                            'query': search_string,
                        },
                    },
                ],
            }
        },
        'sort': {
            'date': {
                'order': 'desc',
            },
        },
        'size': 5000,
        'fields': output_fields,
        '_source': False,
    }

    if course_code is not None:
        query['query']['bool']['must'].append({
            'match_phrase': {
                'courses': course_code,
            }
        })

    if no_course is True:
        query['query']['bool']['must'].append({
            'term': {
                'no_course': True,
            }
        })

    if apply_filter:
        query['query']['bool']['must'].append({
            'multi_match': {
                'query': search_string,
                'fields': [
                    'title',
                    'title.standard',
                ],
                'type': 'bool_prefix',
                'operator': 'and',
            },
        })

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
