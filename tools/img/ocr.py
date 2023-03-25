from typing import Tuple
import requests
import json
import time

from config.settings import settings
from db.models import MathpixRequest

MATHPIX_ENDPOINT = 'https://api.mathpix.com/v3/text'

MATHPIX_PARAMS = {
    'src': '',
    'rm_spaces': True,
    'math_inline_delimiters': [
        '$',
        '$'
    ]
}


class MathpixException(Exception):
    pass


def get_text_content(image_url: str) -> Tuple[str, MathpixRequest]:
    start_time = time.perf_counter()

    params = MATHPIX_PARAMS
    params['src'] = image_url
    response = requests.post(
        url=MATHPIX_ENDPOINT,
        headers={
            'App_id': settings.MATHPIX_APP_ID,
            'App_key': settings.MATHPIX_APP_KEY,
            'Content-Type': 'application/json',
        },
        data=json.dumps(params)
    )

    data = response.json()

    if 'error' in data:
        raise MathpixException(data['error'])

    end_time = time.perf_counter()
    took_ms = int((end_time - start_time) * 1000)

    request = MathpixRequest(
        took_ms=took_ms,
        request_id=data['request_id'],
        version=data['version'],
        image_width=data['image_width'],
        image_height=data['image_height'],
        is_printed=data['is_printed'],
        is_handwritten=data['is_handwritten'],
        confidence=data['confidence'],
        confidence_rate=data['confidence_rate'],
    )

    return (data['text'], request)
