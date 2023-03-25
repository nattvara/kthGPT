from unittest.mock import call
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
        'is_printed': True,
        'is_handwritten': False,
        'confidence': 0.99951171875,
        'text': 'E=mc^2'
    }
    requests_mock = mocker.patch('requests.post', return_value=mock_response)

    parse_image_content.job(image_upload.public_id)

    image_upload.refresh()

    assert image_upload.text_content == 'E=mc^2'

    # Request should include reachable link to the image
    assert requests_mock.call_count == 1
    mathpix_data = MATHPIX_PARAMS
    mathpix_data['src'] = f'{TEST_API_ENDPOINT}/search/image/{image_upload.public_id}'
    assert requests_mock.mock_calls[0] == call(
        url='https://api.mathpix.com/v3/text',
        headers={
            'App_id': TEST_MATHPIX_APP_ID,
            'App_key': TEST_MATHPIX_APP_KEY,
            'Content-Type': 'application/json',
        },
        data=json.dumps(mathpix_data)
    )
