from fastapi import Depends, APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from api.routers.lectures import LectureSummaryOutputModel
import index.courses as courses_index
import index.lecture as lecture_index
from db import get_db

router = APIRouter()


class InputModelSearchCourse(BaseModel):
    query: str
    limit: Optional[int] = None


class CourseOutputModel(BaseModel):
    course_code: str
    display_name: str
    lectures: Optional[int] = None


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
def search_lecture(
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
