from fastapi import Depends, APIRouter, HTTPException, Response
from urllib.parse import urlparse
from pydantic import BaseModel
import logging

from db.crud import (
    get_lecture_by_public_id_and_language,
    get_query_by_sha,
    create_query,
)
import tools.text.prompts as prompts
from config.logger import log
from db.models import Query
import tools.text.ai as ai
from db import get_db


router = APIRouter()


class InputModel(BaseModel):
    lecture_id: str
    language: str
    query_string: str


@router.post('/query', dependencies=[Depends(get_db)])
def new_query(input_data: InputModel) -> Response:
    lecture = get_lecture_by_public_id_and_language(
        input_data.lecture_id,
        input_data.language
    )

    if lecture is None:
        raise HTTPException(status_code=404)

    query = get_query_by_sha(lecture, Query.make_sha(input_data.query_string))
    if query is None:
        query = create_query(lecture, input_data.query_string)

    if query.response is None:
        prompt = prompts.create_query_text(query, lecture)

        try:
            response = ai.gpt3(prompt)
        except Exception as e:
            log().error(e)
            raise HTTPException(
                status_code=500,
                detail='Something went wrong when running GPT-3 query'
            )

        query.response = response
        query.save()

    return Response(
        content=query.response,
        media_type='text/plain'
    )
