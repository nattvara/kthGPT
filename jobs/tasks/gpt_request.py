from rq import Queue, Retry
from typing import Optional
from redis import Redis
import logging

from db.crud import (
    save_message_for_analysis
)
from tools.text.openai import completion
from db.models.analysis import Analysis
from config.settings import settings
from db.models import Lecture
import jobs.tasks.gpt_request


def job(prompt: str, analysis_id: Optional[int] = None, query_id: Optional[int] = None):
    logger = logging.getLogger('rq.worker')
    try:
        response, usage = completion(prompt)

        if analysis_id is not None:
            usage.analysis_id = analysis_id

        if query_id is not None:
            usage.query_id = query_id

        usage.save()

    except Exception as e:
        logger.error(e)
        if analysis_id is not None:
            analysis = Analysis.get(analysis_id)
            save_message_for_analysis(analysis, 'OpenAI Error', 'GPT-3 Error from OpenAI, it is likely overloaded. Retrying in a little while...')  # noqa: E501
        raise e
    return response


# Test run the job
if __name__ == '__main__':
    queue = Queue('gpt', connection=Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
    ))
    j = queue.enqueue(
        jobs.tasks.gpt_request.job,
        'say hello',
        'ev_wkULk2sk',
        Lecture.Language.SWEDISH,
        ttl=15,
        retry=Retry(max=2, interval=[5, 5]),
    )
    print(j.id)
