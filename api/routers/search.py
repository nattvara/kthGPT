from fastapi import Depends, APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from api.routers.lectures import LectureSummaryOutputModel
from db.models import ImageQuestion, ImageQuestionHit
import index.courses as courses_index
import tools.text.prompts as prompts
from db.models import Lecture
from config.logger import log
from db import get_db
import index.lecture
import tools.text.ai
from db.crud import (
    get_lecture_by_public_id_and_language,
    get_image_question_hit_by_public_id,
    get_image_upload_by_public_id,
    get_lecture_by_id,
)

MAX_NUMBER_IMAGE_HITS = 10

router = APIRouter()


class InputModelSearchCourse(BaseModel):
    query: str
    limit: Optional[int] = None


class InputModelSearchCourseCode(BaseModel):
    query: str
    source: Optional[str]
    group: Optional[str]


class CourseOutputModel(BaseModel):
    course_code: str
    display_name: str
    lectures: Optional[int] = None


class InputModelImageQuestion(BaseModel):
    query: str


class HitOutputModel(BaseModel):
    id: str
    answer: Optional[str] = None
    relevance: Optional[str] = None
    lecture: Optional[LectureSummaryOutputModel]


class ImageQuestionOutputModel(BaseModel):
    id: str
    hits: List[HitOutputModel]


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
            source=input_data.source,
            group=input_data.group,
        )
        # Include kth_raw in kth searches
        if input_data.source == Lecture.Source.KTH:
            kth_raw_response = index.lecture.search_in_course(
                input_data.query,
                no_course=True,
                apply_filter=apply_filter,
                source=Lecture.Source.KTH_RAW,
                group=input_data.group,
            )
            response = response + kth_raw_response
        return response

    response = index.lecture.search_in_course(
        input_data.query,
        course_code,
        apply_filter=apply_filter,
        source=input_data.source,
        group=input_data.group,
    )
    # Include kth_raw in kth searches
    if input_data.source == Lecture.Source.KTH:
        kth_raw_response = index.lecture.search_in_course(
            input_data.query,
            course_code,
            apply_filter=apply_filter,
            source=Lecture.Source.KTH_RAW,
            group=input_data.group,
        )
        response = response + kth_raw_response

    return response


@router.post('/search/lecture', dependencies=[Depends(get_db)])
def search_lecture(input_data: InputModelSearchCourseCode) -> List[LectureSummaryOutputModel]:
    response = index.lecture.search_in_transcripts_and_titles(
        input_data.query,
    )

    return response


@router.post('/search/image/{image_public_id}/questions', dependencies=[Depends(get_db)])
def create_image_question(
    image_public_id: str,
    input_data: InputModelImageQuestion
) -> ImageQuestionOutputModel:
    upload = get_image_upload_by_public_id(image_public_id)

    if upload is None:
        raise HTTPException(status_code=404)

    if not upload.parse_image_upload_complete():
        raise HTTPException(status_code=409, detail='image has not finished parsing so question cannot be created, try again later.')  # noqa: E501

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
        log().info(f'searching for (sv): {query}')
        hits = index.lecture.search_in_transcripts_and_titles(query, include_id=True, include_score=True)
        add_hits_to_docs(hits)

    for query in upload.get_search_queries_en():
        log().info(f'searching for (en): {query}')
        hits = index.lecture.search_in_transcripts_and_titles(query, include_id=True, include_score=True)
        add_hits_to_docs(hits)

    total = {}
    for doc in docs:
        total[doc] = sum(docs[doc])

    sorted_docs = sorted(total.items(), key=lambda x: x[1], reverse=True)
    lectures = []
    for (id, _) in sorted_docs:
        if len(lectures) >= MAX_NUMBER_IMAGE_HITS:
            break

        lecture = get_lecture_by_id(id)
        lectures.append(lecture)

    hits = []
    for lecture in lectures:
        hit = ImageQuestionHit(
            public_id=ImageQuestionHit.make_public_id(),
            image_question_id=question.id,
            lecture_id=lecture.id,
        )
        hit.save()
        hits.append(hit.to_dict())

    return {
        'id': question.public_id,
        'hits': hits,
    }


@router.get('/search/image/{image_public_id}/questions/{question_public_id}/hits/{question_hit_public_id}/answer', dependencies=[Depends(get_db)])  # noqa: E501
def get_answer_to_question_hit(
    image_public_id: str,
    question_public_id: str,
    question_hit_public_id: str,
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

    hit = get_image_question_hit_by_public_id(question_hit_public_id)
    if hit is None:
        raise HTTPException(status_code=404)

    hit.create_answer(tools.text.ai, prompts)
    hit.save()

    return {
        'answer': hit.answer,
    }


@router.get('/search/image/{image_public_id}/questions/{question_public_id}/hits/{question_hit_public_id}/relevance', dependencies=[Depends(get_db)])  # noqa: E501
def get_relevance_of_question_hit(
    image_public_id: str,
    question_public_id: str,
    question_hit_public_id: str,
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

    hit = get_image_question_hit_by_public_id(question_hit_public_id)
    if hit is None:
        raise HTTPException(status_code=404)

    hit.create_relevance(tools.text.ai, prompts)
    hit.save()

    return {
        'relevance': hit.relevance,
    }
