import logging
import json

import tools.text.prompts
from db.crud import (
    get_image_upload_by_public_id
)
import tools.text.ai


def job(image_id: str, language: str):
    logger = logging.getLogger('rq.worker')

    upload = get_image_upload_by_public_id(image_id)
    if upload is None:
        raise ValueError(f'image {image_id} was not found')

    try:
        if language == upload.Language.ENGLISH:
            prompt = tools.text.prompts.create_search_query_for_upload_english(upload)
        elif language == upload.Language.SWEDISH:
            prompt = tools.text.prompts.create_search_query_for_upload_swedish(upload)
        else:
            raise ValueError(f'language {language} is not supported')

        response = tools.text.ai.gpt3(
            prompt,
            time_to_live=60 * 2,  # 2 mins
            max_retries=5,
            retry_interval=[
                5,
                10,
                10,
                30,
                30,
            ],
            upload_id=upload.id,
        )

        queries = []
        for query in response.split('\n'):
            query = query.strip()
            if query != '':
                logger.info(f'query {language}: {query}')
                queries.append(query)

        if language == upload.Language.ENGLISH:
            upload.search_queries_en = json.dumps(queries)
            upload.create_search_queries_en_ok = True
            upload.create_search_queries_en_failure_reason = None
            upload.save()
        elif language == upload.Language.SWEDISH:
            upload.search_queries_sv = json.dumps(queries)
            upload.create_search_queries_sv_ok = True
            upload.create_search_queries_sv_failure_reason = None
            upload.save()
        else:
            raise ValueError(f'language {language} is not supported')
    except Exception as e:
        if language == upload.Language.ENGLISH:
            upload.create_search_queries_en_ok = False
            upload.create_search_queries_en_failure_reason = str(e)
            upload.save()
        elif language == upload.Language.SWEDISH:
            upload.create_search_queries_sv_ok = False
            upload.create_search_queries_sv_failure_reason = str(e)
            upload.save()
        raise e
