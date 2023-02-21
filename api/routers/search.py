from typing import List, Optional
from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel

from index.courses import wildcard_search
from db import get_db

router = APIRouter()


class InputModel(BaseModel):
    query: str
    limit: Optional[int] = None


class CourseOutputModel(BaseModel):
    course_code: str
    display_name: str


@router.post('/search/course', dependencies=[Depends(get_db)])
def parse_url(
    input_data: InputModel,
) -> List[CourseOutputModel]:

    if input_data.limit > 40:
        raise HTTPException(status_code=400, detail='Cannot search for that many courses')

    if input_data.query == '':
        return []

    response = wildcard_search(input_data.query, input_data.limit)

    return response
