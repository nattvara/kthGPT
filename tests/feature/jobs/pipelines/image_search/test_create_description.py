from typing import Optional
from rq import Queue

from jobs.pipelines.image_search import (
    create_description
)


def test_create_description_saves_description(mocker, image_upload):
    description = 'this is a math assignment :)'

    mocker.patch('tools.text.ai.gpt3', return_value=description)

    create_description.job(image_upload.public_id)
    image_upload.refresh()

    assert image_upload.description == description
    assert image_upload.create_description_ok is True


def test_create_description_saves_error_on_error(mocker, image_upload):
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
        raise ValueError('wooooups')

    mocker.patch('tools.text.ai.gpt3', side_effect=some_err)

    try:
        create_description.job(image_upload.public_id)
    except Exception:
        pass

    image_upload.refresh()

    assert image_upload.create_description_ok is False
    assert image_upload.create_description_failure_reason == 'wooooups'
