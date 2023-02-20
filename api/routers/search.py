from typing import List
from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel

from index.courses import wildcard_search
from db import get_db

router = APIRouter()


class InputModel(BaseModel):
    query: str


class CourseOutputModel(BaseModel):
    course_code: str
    display_name: str


@router.post('/search/course', dependencies=[Depends(get_db)])
def parse_url(
    input_data: InputModel,
) -> List[CourseOutputModel]:

    response = wildcard_search(input_data.query)

    return response
