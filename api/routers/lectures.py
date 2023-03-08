from fastapi import Depends, APIRouter, HTTPException, Response
from typing import Union, List
from pydantic import BaseModel
import random as rand

from db.models import Analysis
from db import get_db
from db.crud import (
    create_relation_between_lecture_and_course_group,
    find_relation_between_lecture_and_course_group,
    create_relation_between_lecture_and_course,
    find_relation_between_lecture_and_course,
    get_lecture_by_public_id_and_language,
    delete_lecture_course_relation,
    get_all_denied_lectures,
    get_all_failed_lectures,
    get_unfinished_lectures,
    find_course_code,
    get_all_lectures,
)

router = APIRouter()


class MessageOutputModel(BaseModel):
    timestamp: str
    title: str
    body: Union[str, None] = None


class AnalysisOutputModel(BaseModel):
    analysis_id: int
    created_at: str
    modified_at: str
    state: str
    frozen: bool
    last_message: Union[MessageOutputModel, None] = None
    mp4_progress: int
    mp3_progress: int
    transcript_progress: int
    summary_progress: int
    overall_progress: int


class CourseOutputModel(BaseModel):
    course_code: str
    display_name: str


class LectureOutputModel(BaseModel):
    public_id: str
    language: str
    created_at: str
    title: Union[str, None] = None
    date: Union[str, None] = None
    approved: Union[bool, None] = None
    source: str
    words: int
    length: int
    preview_uri: Union[str, None] = None
    preview_small_uri: Union[str, None] = None
    transcript_uri: Union[str, None] = None
    summary_uri: Union[str, None] = None
    content_link: Union[str, None] = None
    analysis: Union[AnalysisOutputModel, None] = None
    courses: List[CourseOutputModel]
    courses_can_change: bool


class LectureSummaryOutputModel(BaseModel):
    public_id: str
    language: str
    source: str
    created_at: Union[str, None] = None
    title: Union[str, None] = None
    date: Union[str, None] = None
    state: Union[str, None] = None
    frozen: Union[bool, None] = None
    content_link: Union[str, None] = None
    preview_uri: Union[str, None] = None
    preview_small_uri: Union[str, None] = None
    overall_progress: Union[int, None] = None


@router.get('/lectures', dependencies=[Depends(get_db)])
def get_all(
    summary: Union[bool, None] = None,
    only_unfinished: Union[bool, None] = None,
    only_denied: Union[bool, None] = None,
    only_failed: Union[bool, None] = None,
    include_denied: Union[bool, None] = False,
    include_failed: Union[bool, None] = False,
    random: Union[bool, None] = None,
) -> List[Union[LectureOutputModel, LectureSummaryOutputModel]]:
    if only_unfinished:
        lectures = get_unfinished_lectures()
    elif only_denied:
        include_denied = True
        lectures = get_all_denied_lectures()
    elif only_failed:
        include_failed = True
        lectures = get_all_failed_lectures()
    else:
        lectures = get_all_lectures()

    out = []
    for lecture in lectures:
        has_analysis = lecture.get_last_analysis() is not None
        if random:
            if not has_analysis:
                continue
            if lecture.get_last_analysis().state != Analysis.State.READY:
                continue

        if not include_denied:
            if not has_analysis:
                continue
            if lecture.get_last_analysis().state == Analysis.State.DENIED:
                continue

        if not include_failed:
            if not has_analysis:
                continue
            if lecture.get_last_analysis().state == Analysis.State.FAILURE:
                continue

        if summary:
            out.append(lecture.to_summary_dict())
        else:
            out.append(lecture.to_dict())

    if random and len(out) == 0:
        return []

    if random:
        index = rand.randint(0, len(out) - 1)
        return [out[index]]

    if summary:
        out.reverse()

    return out


@router.get('/lectures/{public_id}/{language}', dependencies=[Depends(get_db)])
def get_lecture(public_id: str, language: str):
    lecture = get_lecture_by_public_id_and_language(public_id, language)
    if lecture is None:
        raise HTTPException(status_code=404)

    return lecture.to_dict()


@router.get('/lectures/{public_id}/{language}/preview', dependencies=[Depends(get_db)])
def get_preview(public_id: str, language: str):
    lecture = get_lecture_by_public_id_and_language(public_id, language)
    if lecture is None:
        raise HTTPException(status_code=404)

    if lecture.img_preview is None:
        raise HTTPException(status_code=404)

    with open(lecture.img_preview, 'rb') as file:
        image_bytes: bytes = file.read()
        return Response(content=image_bytes, media_type='image/png')


@router.get('/lectures/{public_id}/{language}/preview-small', dependencies=[Depends(get_db)])
def get_small_preview(public_id: str, language: str):
    lecture = get_lecture_by_public_id_and_language(public_id, language)
    if lecture is None:
        raise HTTPException(status_code=404)

    if lecture.img_preview_small is None:
        raise HTTPException(status_code=404)

    with open(lecture.img_preview_small, 'rb') as file:
        image_bytes: bytes = file.read()
        return Response(content=image_bytes, media_type='image/png')


@router.get('/lectures/{public_id}/{language}/transcript', dependencies=[Depends(get_db)])
def get_transcript(public_id: str, language: str):
    lecture = get_lecture_by_public_id_and_language(public_id, language)
    if lecture is None:
        raise HTTPException(status_code=404)

    if lecture.transcript_filepath is None:
        raise HTTPException(status_code=404)

    return Response(
        content=lecture.transcript_text(),
        media_type='text/plain'
    )


@router.get('/lectures/{public_id}/{language}/summary', dependencies=[Depends(get_db)])
def get_summary(public_id: str, language: str):
    lecture = get_lecture_by_public_id_and_language(public_id, language)
    if lecture is None:
        raise HTTPException(status_code=404)

    if lecture.summary_filepath is None:
        raise HTTPException(status_code=404)

    return Response(
        content=lecture.summary_text(),
        media_type='text/plain'
    )


class PostCourseInputModel(BaseModel):
    course_code: str


@router.post('/lectures/{public_id}/{language}/course', dependencies=[Depends(get_db)])
def add_course_to_lecture(public_id: str, language: str, input_data: PostCourseInputModel) -> LectureOutputModel:
    lecture = get_lecture_by_public_id_and_language(public_id, language)
    if lecture is None:
        raise HTTPException(status_code=404)

    if not lecture.courses_can_be_changed():
        raise HTTPException(status_code=400, detail='A lectures courses can only be changed within the first day of being added')  # noqa: E501

    code = input_data.course_code

    course = find_course_code(code)
    if course is None:
        raise HTTPException(status_code=400, detail='invalid course code')

    if lecture.has_course(code):
        return lecture.to_dict()

    limit = 10
    if len(lecture.courses()) >= limit:
        raise HTTPException(status_code=400, detail=f'Too many courses. A lecture cannot have more than {limit} courses.')

    if course.source == course.Source.COURSE_GROUP:
        create_relation_between_lecture_and_course_group(lecture.id, course.course_group_id)
    elif course.source == course.Source.COURSE:
        create_relation_between_lecture_and_course(lecture.id, course.course_id)

    lecture.reindex()
    course.reindex()

    return lecture.to_dict()


@router.delete('/lectures/{public_id}/{language}/course/{course_code}', dependencies=[Depends(get_db)])
def remove_course_to_lecture(public_id: str, language: str, course_code: str) -> LectureOutputModel:
    lecture = get_lecture_by_public_id_and_language(public_id, language)
    if lecture is None:
        raise HTTPException(status_code=404)

    if not lecture.courses_can_be_changed():
        raise HTTPException(status_code=400, detail='A lectures courses can only be changed within the first day of being added')  # noqa: E501

    course = find_course_code(course_code)
    if course is None:
        raise HTTPException(status_code=400, detail='invalid course code')

    if not lecture.has_course(course_code):
        raise HTTPException(status_code=404)

    if course.source == course.Source.COURSE_GROUP:
        relation = find_relation_between_lecture_and_course_group(lecture.id, course.course_group_id)
    elif course.source == course.Source.COURSE:
        relation = find_relation_between_lecture_and_course(lecture.id, course.course_id)

    delete_lecture_course_relation(relation.id)

    lecture.reindex()
    course.reindex()

    return lecture.to_dict()
