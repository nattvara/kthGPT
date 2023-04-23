from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel

from db import get_db
from db.crud import (
    find_course_code,
)

router = APIRouter()


class CourseOutputModel(BaseModel):
    course_code: str
    display_name: str


@router.get('/courses/{course_code}', dependencies=[Depends(get_db)])
def get_course(course_code: str) -> CourseOutputModel:
    if course_code == 'no_course':
        return {
            'course_code': 'no_course',
            'display_name': 'Untagged Lectures',
        }

    course = find_course_code(course_code)
    if course is None:
        raise HTTPException(status_code=404)

    return course.to_small_dict()
