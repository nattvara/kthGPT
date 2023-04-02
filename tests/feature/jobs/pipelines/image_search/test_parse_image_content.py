from unittest.mock import call
from decimal import Decimal
import json

from jobs.pipelines.image_search import (
    parse_image_content
)
from tests.conftest import (
    TEST_API_ENDPOINT,
    TEST_MATHPIX_APP_ID,
    TEST_MATHPIX_APP_KEY
)
from tools.img.ocr import (
    MATHPIX_PARAMS
)


def test_parse_image_job_sends_request_to_mathpix(mocker, image_upload):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'request_id': 'some_id',
        'version': 'RSK-M111p1',
        'image_width': 100,
        'image_height': 200,
        'is_printed': True,
        'is_handwritten': False,
        'auto_rotate_confidence': 0,
        'auto_rotate_degrees': 0,
        'confidence': 0.99951171875,
        'confidence_rate': 0.9999023246709239,
        'text': 'E=mc^2'
    }
    requests_mock = mocker.patch('requests.post', return_value=mock_response)

    parse_image_content.job(image_upload.public_id)

    image_upload.refresh()

    assert image_upload.text_content == 'E=mc^2'
    assert image_upload.parse_image_content_ok is True

    # Request should include reachable link to the image
    assert requests_mock.call_count == 1
    mathpix_data = MATHPIX_PARAMS
    mathpix_data['src'] = f'{TEST_API_ENDPOINT}search/image/{image_upload.public_id}/img'
    assert requests_mock.mock_calls[0] == call(
        url='https://api.mathpix.com/v3/text',
        headers={
            'App_id': TEST_MATHPIX_APP_ID,
            'App_key': TEST_MATHPIX_APP_KEY,
            'Content-Type': 'application/json',
        },
        data=json.dumps(mathpix_data)
    )


def test_parse_image_job_saves_mathpix_metadata(mocker, image_upload):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'request_id': 'some_id',
        'version': 'RSK-M111p1',
        'image_width': 100,
        'image_height': 200,
        'is_printed': True,
        'is_handwritten': False,
        'auto_rotate_confidence': 0,
        'auto_rotate_degrees': 0,
        'confidence': 0.99951171875,
        'confidence_rate': 0.9999023246709239,
        'text': 'E=mc^2'
    }
    mocker.patch('requests.post', return_value=mock_response)

    parse_image_content.job(image_upload.public_id)
    image_upload.refresh()

    requests = image_upload.mathpix_requests()

    assert len(requests) == 1
    assert requests[0].request_id == 'some_id'
    assert requests[0].version == 'RSK-M111p1'
    assert requests[0].image_width == 100
    assert requests[0].image_height == 200
    assert requests[0].is_printed is True
    assert requests[0].is_handwritten is False
    assert requests[0].confidence == Decimal('0.99951171875')
    assert requests[0].confidence_rate == Decimal('0.9999023246709239')


def test_parse_image_job_saves_error_on_mathpix_error(mocker, image_upload):
    mock_response = mocker.Mock()
    mock_response.status_code = 200  # for some reason actually does respond with a 200 when there is an error
    mock_response.json.return_value = {
        'request_id': 'some_id',
        'version': 'RSK-M112',
        'error': 'Cannot read image',
        'error_info': {
            'id': 'image_decode_error',
            'message': 'Cannot read image'
        }
    }
    mocker.patch('requests.post', return_value=mock_response)

    try:
        parse_image_content.job(image_upload.public_id)
    except Exception:
        pass

    image_upload.refresh()

    assert image_upload.parse_image_content_ok is False
    assert image_upload.parse_image_content_failure_reason == 'Cannot read image'
