from fastapi import Depends, APIRouter
from pydantic import BaseModel

import index.courses as courses_index
import index.lecture as lecture_index
from db import get_db

router = APIRouter()


class StatsOutputModel(BaseModel):
    courses: int
    lectures: int
    lectures_without_courses: int


@router.get('/stats', dependencies=[Depends(get_db)])
def get_stats() -> StatsOutputModel:
    return {
        'courses': courses_index.at_least_one_lecture_count(),
        'lectures': lecture_index.match_all_count(),
        'lectures_without_courses': lecture_index.term_query_no_courses_count(),
    }
