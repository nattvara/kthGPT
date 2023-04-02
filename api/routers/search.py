from fastapi import Depends, APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel
import os

from tools.files.paths import get_sha_of_binary_file_descriptor
from api.routers.lectures import LectureSummaryOutputModel
from db.models import ImageUpload, ImageQuestion
import index.courses as courses_index
import tools.text.prompts as prompts
import index.lecture
from db import get_db
import tools.text.ai
from db.crud import (
    get_lecture_by_public_id_and_language,
    get_image_upload_by_image_sha,
    get_image_upload_by_public_id,
    get_lecture_by_id,
)
import jobs

MAX_NUMBER_IMAGE_HITS = 6

router = APIRouter()


class InputModelSearchCourse(BaseModel):
    query: str
    limit: Optional[int] = None


class InputModelSearchCourseCode(BaseModel):
    query: str


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
    parse_image_content_ok: Optional[bool]
    create_description_ok: Optional[bool]
    create_search_queries_en_ok: Optional[bool]
    create_search_queries_sv_ok: Optional[bool]


class InputModelImageQuestion(BaseModel):
    query: str


class ImageQuestionOutputModel(BaseModel):
    id: str
    hits: List[LectureSummaryOutputModel]


class LectureAnswerOutputModel(BaseModel):
    answer: str


class LectureRelevanceOutputModel(BaseModel):
    relevance: str


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


@router.post('/search/course/{course_code}', dependencies=[Depends(get_db)])
def search_course_lectures(
    course_code: str,
    input_data: InputModelSearchCourseCode,
) -> List[LectureSummaryOutputModel]:

    apply_filter = True
    if input_data.query == '':
        apply_filter = False

    if course_code == 'no_course':
        response = index.lecture.search_in_course(
            input_data.query,
            no_course=True,
            apply_filter=apply_filter,
        )
        return response

    response = index.lecture.search_in_course(
        input_data.query,
        course_code,
        apply_filter,
    )

    return response


@router.post('/search/lecture', dependencies=[Depends(get_db)])
def search_lecture(input_data: InputModelSearchCourseCode) -> List[LectureSummaryOutputModel]:
    response = index.lecture.search_in_transcripts_and_titles(
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

    sha = get_sha_of_binary_file_descriptor(file.file)
    image = get_image_upload_by_image_sha(sha)
    should_start_image_search_pipeline = False

    if image is None:
        should_start_image_search_pipeline = True
        image = ImageUpload(
            public_id=ImageUpload.make_public_id(),
            file_format=extension,
        )
        image.save()

        image.save_image_data(file)

    if not image.parse_image_content_ok:
        should_start_image_search_pipeline = True

    if not image.create_description_ok:
        should_start_image_search_pipeline = True

    if not image.create_search_queries_en_ok:
        should_start_image_search_pipeline = True

    if not image.create_search_queries_sv_ok:
        should_start_image_search_pipeline = True

    if should_start_image_search_pipeline:
        jobs.schedule_image_search(image)

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


@router.post('/search/image/{image_public_id}/questions', dependencies=[Depends(get_db)])
def create_image_question(
    image_public_id: str,
    input_data: InputModelImageQuestion
) -> ImageQuestionOutputModel:
    upload = get_image_upload_by_public_id(image_public_id)

    if upload is None:
        raise HTTPException(status_code=404)

    question = ImageQuestion(
        public_id=ImageQuestion.make_public_id(),
        image_upload_id=upload.id,
        query_string=input_data.query,
    )
    question.save()

    docs = {}

    def add_hits_to_docs(hits: list):
        for hit in hits:
            if hit['_id'] not in docs:
                docs[hit['_id']] = []
            docs[hit['_id']].append(hit['_score'])

    for query in upload.get_search_queries_sv():
        hits = index.lecture.search_in_transcripts_and_titles(query, include_id=True, include_score=True)
        add_hits_to_docs(hits)

    for query in upload.get_search_queries_en():
        hits = index.lecture.search_in_transcripts_and_titles(query, include_id=True, include_score=True)
        add_hits_to_docs(hits)

    total = {}
    for doc in docs:
        total[doc] = sum(docs[doc])

    sorted_docs = sorted(total.items(), key=lambda x: x[1], reverse=True)
    top_docs = sorted_docs[:MAX_NUMBER_IMAGE_HITS]

    lectures = []
    for (id, _) in top_docs:
        lectures.append(get_lecture_by_id(id).to_dict())

    return {
        'id': question.public_id,
        'hits': lectures,
    }


@router.get('/search/image/{image_public_id}/questions/{question_public_id}/{lecture_public_id}/{lecture_language}/answer', dependencies=[Depends(get_db)])
def get_answer_to_question_hit(
    image_public_id: str,
    question_public_id: str,
    lecture_public_id: str,
    lecture_language: str,
) -> LectureAnswerOutputModel:
    upload = get_image_upload_by_public_id(image_public_id)

    if upload is None:
        raise HTTPException(status_code=404)

    question = None
    for q in upload.questions():
        if q.public_id == question_public_id:
            question = q

    if question is None:
        raise HTTPException(status_code=404)

    lecture = get_lecture_by_public_id_and_language(
        lecture_public_id,
        lecture_language,
    )
    if lecture is None:
        raise HTTPException(status_code=404)

    prompt = prompts.create_prompt_to_answer_question_about_hit(
        lecture,
        upload,
        question,
    )
    response = tools.text.ai.gpt3(
        prompt,
        time_to_live=60,
        max_retries=2,
        retry_interval=[10, 20],
        upload_id=upload.id,
    )

    return {
        'answer': response,
    }


@router.get('/search/image/{image_public_id}/questions/{question_public_id}/{lecture_public_id}/{lecture_language}/relevance', dependencies=[Depends(get_db)])
def get_relevance_of_question_hit(
    image_public_id: str,
    question_public_id: str,
    lecture_public_id: str,
    lecture_language: str,
) -> LectureRelevanceOutputModel:
    upload = get_image_upload_by_public_id(image_public_id)

    if upload is None:
        raise HTTPException(status_code=404)

    question = None
    for q in upload.questions():
        if q.public_id == question_public_id:
            question = q

    if question is None:
        raise HTTPException(status_code=404)

    lecture = get_lecture_by_public_id_and_language(
        lecture_public_id,
        lecture_language,
    )
    if lecture is None:
        raise HTTPException(status_code=404)

    prompt = prompts.create_prompt_to_explain_hit_relevance(
        lecture,
        upload,
        question,
    )
    response = tools.text.ai.gpt3(
        prompt,
        time_to_live=60,
        max_retries=2,
        retry_interval=[10, 20],
        upload_id=upload.id,
    )

    return {
        'relevance': response,
    }
