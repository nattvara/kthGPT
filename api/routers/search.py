from fastapi import Depends, APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel
import os

from api.routers.lectures import LectureSummaryOutputModel
from db.crud import get_image_upload_by_public_id
import index.courses as courses_index
import index.lecture as lecture_index
from db.models import ImageUpload
from db import get_db
import jobs

router = APIRouter()


class InputModelSearchCourse(BaseModel):
    query: str
    limit: Optional[int] = None


class CourseOutputModel(BaseModel):
    course_code: str
    display_name: str
    lectures: Optional[int] = None


class ImageCreationOutputModel(BaseModel):
    id: str


class ImageOutputModel(BaseModel):
    id: str
    created_at: str
    modified_at: str
    text_content: Optional[str]
    description: Optional[str]


@router.post('/search/course', dependencies=[Depends(get_db)])
def search_course(
    input_data: InputModelSearchCourse,
    include_lectures: Optional[bool] = None,
    lecture_count_above_or_equal: Optional[int] = 0,
) -> List[CourseOutputModel]:

    sort_by_lecture_count = False
    unlimited = False
    if lecture_count_above_or_equal >= 1:
        unlimited = True
        sort_by_lecture_count = True

    if not unlimited:
        if input_data.limit is None:
            raise HTTPException(status_code=400, detail='Please specify a limit to the search result')
        if input_data.limit > 40:
            raise HTTPException(status_code=400, detail='Cannot search for that many courses')

    apply_filter = True
    if input_data.query == '':
        if not unlimited:
            return []

        apply_filter = False

    response = courses_index.wildcard_search(
        input_data.query,
        include_lectures=include_lectures,
        lecture_count_above_or_equal=lecture_count_above_or_equal,
        unlimited=unlimited,
        sort_by_lecture_count=sort_by_lecture_count,
        apply_filter=apply_filter,
    )

    return response


class InputModelSearchCourseCode(BaseModel):
    query: str


@router.post('/search/course/{course_code}', dependencies=[Depends(get_db)])
def search_course_lectures(
    course_code: str,
    input_data: InputModelSearchCourseCode,
) -> List[LectureSummaryOutputModel]:

    apply_filter = True
    if input_data.query == '':
        apply_filter = False

    if course_code == 'no_course':
        response = lecture_index.search_in_course(
            input_data.query,
            no_course=True,
            apply_filter=apply_filter,
        )
        return response

    response = lecture_index.search_in_course(
        input_data.query,
        course_code,
        apply_filter,
    )

    return response


@router.post('/search/lecture', dependencies=[Depends(get_db)])
def search_lecture(input_data: InputModelSearchCourseCode) -> List[LectureSummaryOutputModel]:
    response = lecture_index.search_in_transcripts_and_titles(
        input_data.query,
    )

    return response


@router.post('/search/image', dependencies=[Depends(get_db)])
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
        raise HTTPException(status_code=400, detail='Invalid image format, please provide an image in one of the following formats ' + ', '.join(allowed_extensions))

    image = ImageUpload(
        public_id=ImageUpload.make_public_id(),
        file_format=extension,
    )
    image.save()

    image.save_image_data(file)

    jobs.schedule_image_search(image.public_id)

    return {
        'id': image.public_id,
    }


@router.get('/search/image/{public_id}', dependencies=[Depends(get_db)])
def get_image_info(public_id: str) -> ImageOutputModel:
    upload = get_image_upload_by_public_id(public_id)

    if upload is None:
        raise HTTPException(status_code=404)

    return upload.to_dict()


@router.get('/search/image/{public_id}/img', dependencies=[Depends(get_db)])
def get_image_data(public_id: str) -> FileResponse:
    upload = get_image_upload_by_public_id(public_id)

    if upload is None:
        raise HTTPException(status_code=404)

    return FileResponse(upload.get_filename())
