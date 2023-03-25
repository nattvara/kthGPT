import logging

from tools.img.ocr import get_text_content
from config.settings import settings
from db.models import ImageUpload
from db.crud import (
    get_image_upload_by_public_id
)


def make_img_url(upload: ImageUpload) -> str:
    return f'{settings.API_ENDPOINT}search/image/{upload.public_id}/img'


def job(image_id: str):
    upload = get_image_upload_by_public_id(image_id)
    if upload is None:
        raise ValueError(f'image {image_id} was not found')

    try:
        text_content, request = get_text_content(make_img_url(upload))
        upload.text_content = text_content
        upload.parse_image_content_ok = True
        upload.save()

        request.image_upload_id = upload.id
        request.save()

    except Exception as e:
        upload.parse_image_content_ok = False
        upload.parse_image_content_failure_reason = str(e)
        upload.save()
        raise e
