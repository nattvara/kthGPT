import requests
import json

from config.settings import settings

MATHPIX_ENDPOINT = 'https://api.mathpix.com/v3/text'

MATHPIX_PARAMS = {
    'src': '',
    'rm_spaces': True,
    'math_inline_delimiters': [
        '$',
        '$'
    ]
}


def get_text_content(image_url: str):
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

    return response.json()['text']
