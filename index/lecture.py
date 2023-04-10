from typing import Optional

from . import client, clean_response
from db.models import Lecture


INDEX_NAME = 'lecture'

LECTURE_OUTPUT_FIELDS = [
    'public_id',
    'language',
    'approved',
    'source',
    'date',
    'words',
    'length',
    'title',
    'group',
    'description',
    'title.standard',
    'preview_uri',
    'preview_small_uri',
    'content_link',
    'courses',
]


def clean():
    client.indices.delete(
        index=INDEX_NAME,
        ignore=[400, 404],
    )


def create():
    index_body = {
        'settings': {
            'index': {
                'number_of_shards': 1,
                'number_of_replicas': 0,
            },
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


def search_in_course(
    search_string: str,
    course_code: Optional[str] = None,
    source: Optional[str] = None,
    group: Optional[str] = None,
    apply_filter: Optional[bool] = True,
    no_course: Optional[bool] = False,
):
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
        'fields': LECTURE_OUTPUT_FIELDS,
        '_source': False,
    }

    if course_code is not None:
        query['query']['bool']['must'].append({
            'match_phrase': {
                'courses': course_code,
            }
        })

    if source is not None:
        query['query']['bool']['must'].append({
            'match_phrase': {
                'source': source,
            }
        })

    if group is not None:
        query['query']['bool']['must'].append({
            'match_phrase': {
                'group': group,
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

    return clean_response(response, LECTURE_OUTPUT_FIELDS)


def search_in_transcripts_and_titles(search_string: str, include_id=False, include_score=False):
    query = {
        'query': {
            'multi_match': {
                'query': search_string,
                'fields': [
                    'title',
                    'transcript',
                ],
            }
        },
        'highlight': {
            'number_of_fragments': 3,
            'fragment_size': 150,
            'fields': {
                'transcript': {
                    'pre_tags': ['<strong>'],
                    'post_tags': ['</strong>'],
                },
                'title': {
                    'pre_tags': ['<strong>'],
                    'post_tags': ['</strong>'],
                    'number_of_fragments': 0
                },
            }
        },
        'size': 10,
        'fields': LECTURE_OUTPUT_FIELDS,
        '_source': False,
    }

    response = client.search(
        index=INDEX_NAME,
        body=query,
    )

    return clean_response(response, LECTURE_OUTPUT_FIELDS, include_id=include_id, include_score=include_score)


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
