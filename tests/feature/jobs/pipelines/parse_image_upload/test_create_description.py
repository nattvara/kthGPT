from typing import Optional
from rq import Queue

from jobs.pipelines.parse_image_upload import (
    create_description
)


def test_create_description_saves_english_description(mocker, image_upload):
    description = 'this is a math assignment :)'

    mocker.patch('tools.text.ai.gpt3', return_value=description)

    create_description.job(image_upload.public_id, image_upload.Language.ENGLISH)
    image_upload.refresh()

    assert image_upload.description_en == description
    assert image_upload.create_description_en_ok is True


def test_create_description_saves_swedish_description(mocker, image_upload):
    description = 'skriv ett utryck för volymen av en köttbulle'

    mocker.patch('tools.text.ai.gpt3', return_value=description)

    create_description.job(image_upload.public_id, image_upload.Language.SWEDISH)
    image_upload.refresh()

    assert image_upload.description_sv == description
    assert image_upload.create_description_sv_ok is True


def test_create_description_saves_error_on_english_error(mocker, image_upload):
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
        create_description.job(image_upload.public_id, image_upload.Language.ENGLISH)
    except Exception:
        pass

    image_upload.refresh()

    assert image_upload.create_description_en_ok is False
    assert image_upload.create_description_en_failure_reason == 'wooooups'


def test_create_description_saves_error_on_swedish_error(mocker, image_upload):
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
        create_description.job(image_upload.public_id, image_upload.Language.SWEDISH)
    except Exception:
        pass

    image_upload.refresh()

    assert image_upload.create_description_sv_ok is False
    assert image_upload.create_description_sv_failure_reason == 'wooooups'
