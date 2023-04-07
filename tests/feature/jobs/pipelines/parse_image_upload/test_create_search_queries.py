from typing import Optional
from rq import Queue

from jobs.pipelines.parse_image_upload import (
    create_search_queries
)


def test_create_search_queries_can_save_english_queries(mocker, image_upload):
    response = '''
english query 1
english query 2
'''.strip()

    mocker.patch('tools.text.ai.gpt3', return_value=response)

    create_search_queries.job(image_upload.public_id, image_upload.Language.ENGLISH)
    image_upload.refresh()

    assert image_upload.get_search_queries_en() == [
        'english query 1',
        'english query 2',
    ]
    assert image_upload.create_search_queries_en_ok is True


def test_create_search_queries_saves_error_on_failure_to_create_english_queries(mocker, image_upload):
    def some_err(
        prompt: str,
        time_to_live: int = 60,
        max_retries: int = 3,
        retry_interval: list = [10, 30, 60],
        queue_approval: Queue = None,
        analysis_id: Optional[int] = None,
        query_id: Optional[int] = None,
        upload_id: Optional[int] = None,
    ):
        raise ValueError('wooooupsie')

    mocker.patch('tools.text.ai.gpt3', side_effect=some_err)

    try:
        create_search_queries.job(image_upload.public_id, image_upload.Language.ENGLISH)
    except Exception:
        pass

    image_upload.refresh()

    assert image_upload.create_search_queries_en_ok is False
    assert image_upload.create_search_queries_en_failure_reason == 'wooooupsie'


def test_create_search_queries_can_save_swedish_queries(mocker, image_upload):
    response = '''
svenskt query 1
svenskt query 2
'''.strip()

    mocker.patch('tools.text.ai.gpt3', return_value=response)

    create_search_queries.job(image_upload.public_id, image_upload.Language.SWEDISH)
    image_upload.refresh()

    assert image_upload.get_search_queries_sv() == [
        'svenskt query 1',
        'svenskt query 2',
    ]
    assert image_upload.create_search_queries_sv_ok is True


def test_create_search_queries_saves_error_on_failure_to_create_swedish_queries(mocker, image_upload):
    def some_err(
        prompt: str,
        time_to_live: int = 60,
        max_retries: int = 3,
        retry_interval: list = [10, 30, 60],
        queue_approval: Queue = None,
        analysis_id: Optional[int] = None,
        query_id: Optional[int] = None,
        upload_id: Optional[int] = None,
    ):
        raise ValueError('wooooupsie doopsie')

    mocker.patch('tools.text.ai.gpt3', side_effect=some_err)

    try:
        create_search_queries.job(image_upload.public_id, image_upload.Language.SWEDISH)
    except Exception:
        pass

    image_upload.refresh()

    assert image_upload.create_search_queries_sv_ok is False
    assert image_upload.create_search_queries_sv_failure_reason == 'wooooupsie doopsie'
