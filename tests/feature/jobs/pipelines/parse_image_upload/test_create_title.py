from typing import Optional
from rq import Queue

from jobs.pipelines.parse_image_upload import (
    create_title
)


def test_create_title_job_saves_title(mocker, image_upload):
    title = 'a cool assignment'

    mocker.patch('tools.text.ai.gpt3', return_value=title)

    create_title.job(image_upload.public_id)
    image_upload.refresh()

    assert image_upload.title == title
    assert image_upload.create_title_ok is True


def test_create_title_job_saves_failure_reason_on_error(mocker, image_upload):
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
        create_title.job(image_upload.public_id)
    except Exception:
        pass

    image_upload.refresh()

    assert image_upload.create_title_ok is False
    assert image_upload.create_title_failure_reason == 'wooooups'
