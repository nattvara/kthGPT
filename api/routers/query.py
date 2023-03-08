from typing import Union
from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel

from db.crud import (
    get_lecture_by_public_id_and_language,
    get_most_recent_query_by_sha,
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
    override_cache: Union[bool, None] = None


class OutputModel(BaseModel):
    response: str
    cached: bool


@router.post('/query', dependencies=[Depends(get_db)])
def new_query(input_data: InputModel) -> OutputModel:
    lecture = get_lecture_by_public_id_and_language(
        input_data.lecture_id,
        input_data.language
    )

    if lecture is None:
        raise HTTPException(status_code=404)

    query = get_most_recent_query_by_sha(lecture, Query.make_sha(input_data.query_string))

    cached = True
    should_create_new_query = False

    if query is None:
        should_create_new_query = True

    elif query.response is None:
        should_create_new_query = True

    elif input_data.override_cache:
        should_create_new_query = True

    elif query.cache_is_valid is False:
        should_create_new_query = True

    if should_create_new_query:
        cached = False
        query = create_query(lecture, input_data.query_string)

        if lecture.language == lecture.Language.ENGLISH:
            prompt = prompts.create_query_text_english(query, lecture)
        elif lecture.language == lecture.Language.SWEDISH:
            prompt = prompts.create_query_text_swedish(query, lecture)
        else:
            raise ValueError(f'language {lecture.language} is not supported')

        try:
            response = ai.gpt3(
                prompt,
                time_to_live=60,
                max_retries=2,
                retry_interval=[10, 20],
                query_id=query.id,
            )
        except ai.GPTException as e:
            log().error(e)
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )
        except Exception as e:
            log().error(e)
            raise HTTPException(
                status_code=500,
                detail='Something went wrong when running GPT-3 query'
            )

        query.response = response
        query.save()

    query.count += 1
    query.save()

    return {
        'response': query.response,
        'cached': cached,
    }
