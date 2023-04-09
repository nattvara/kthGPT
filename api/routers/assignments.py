from fastapi import Depends, APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os

from tools.files.paths import get_sha_of_binary_file_descriptor
from db.models import ImageUpload
from db import get_db
from db.crud import (
    get_image_upload_by_image_sha,
    get_image_upload_by_public_id,
)
import jobs

MAX_NUMBER_IMAGE_HITS = 10

router = APIRouter()


class ImageCreationOutputModel(BaseModel):
    id: str


class ImageOutputModel(BaseModel):
    id: str
    created_at: str
    modified_at: str
    text_content: Optional[str]
    title: Optional[str]
    description_en: Optional[str]
    description_sv: Optional[str]
    can_ask_question: bool
    parse_image_upload_complete: bool
    parse_image_content_ok: Optional[bool]
    create_title_ok: Optional[bool]
    create_description_en_ok: Optional[bool]
    create_description_sv_ok: Optional[bool]
    create_search_queries_en_ok: Optional[bool]
    create_search_queries_sv_ok: Optional[bool]


@router.post('/assignments/image', dependencies=[Depends(get_db)])
def search_image(file: UploadFile) -> ImageCreationOutputModel:
    _, extension = os.path.splitext(file.filename)
    extension = extension.replace('.', '')
    extension = extension.lower()

    allowed_extensions = [
        'jpg',
        'jpeg',
        'jji',
        'jpe',
        'jif',
        'jfif',
        'heif',
        'heic',
        'png',
        'gif',
        'webp',
        'tiff',
        'tif',
    ]

    if extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail='Invalid image format, please provide an image in one of the following formats ' + ', '.join(allowed_extensions))  # noqa: E501

    sha = get_sha_of_binary_file_descriptor(file.file)
    image = get_image_upload_by_image_sha(sha)
    should_start_parse_image_upload_pipeline = False

    if image is None:
        should_start_parse_image_upload_pipeline = True
        image = ImageUpload(
            public_id=ImageUpload.make_public_id(),
            file_format=extension,
        )
        image.save()

        image.save_image_data(file)

    if not image.parse_image_content_ok:
        should_start_parse_image_upload_pipeline = True

    if not image.create_description_en_ok:
        should_start_parse_image_upload_pipeline = True

    if not image.create_title_ok:
        should_start_parse_image_upload_pipeline = True

    if not image.create_description_sv_ok:
        should_start_parse_image_upload_pipeline = True

    if not image.create_search_queries_en_ok:
        should_start_parse_image_upload_pipeline = True

    if not image.create_search_queries_sv_ok:
        should_start_parse_image_upload_pipeline = True

    if should_start_parse_image_upload_pipeline:
        jobs.schedule_parse_image_upload(image)

    return {
        'id': image.public_id,
    }


@router.get('/assignments/image/{public_id}', dependencies=[Depends(get_db)])
def get_image_info(public_id: str) -> ImageOutputModel:
    upload = get_image_upload_by_public_id(public_id)

    if upload is None:
        raise HTTPException(status_code=404)

    return upload.to_dict()


@router.post('/assignments/image/{public_id}', dependencies=[Depends(get_db)])
def update_image_upload(
    public_id: str,
    restart: Optional[bool] = None,
) -> ImageOutputModel:
    upload = get_image_upload_by_public_id(public_id)

    if upload is None:
        raise HTTPException(status_code=404)

    if restart and not upload.parse_image_upload_complete():
        upload.clear_parse_results()
        upload.save()
        jobs.schedule_parse_image_upload(upload)

    return upload.to_dict()


@router.get('/assignments/image/{public_id}/img', dependencies=[Depends(get_db)])
def get_image_data(public_id: str) -> FileResponse:
    upload = get_image_upload_by_public_id(public_id)

    if upload is None:
        raise HTTPException(status_code=404)

    return FileResponse(upload.get_filename())
