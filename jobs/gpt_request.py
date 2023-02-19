from rq import Queue, Retry
from redis import Redis
import logging

from db.crud import (
    get_lecture_by_public_id_and_language,
    save_message_for_analysis
)
from tools.text.openai import completion
from config.settings import settings
from db.models import Lecture
import jobs.gpt_request


def job(prompt: str, lecture_id: str = None, language: str = None):
    logger = logging.getLogger('rq.worker')
    try:
        response = completion(prompt)
    except Exception as e:
        logger.error(e)
        if lecture_id is not None:
            lecture = get_lecture_by_public_id_and_language(lecture_id, language)
            if lecture is None:
                raise ValueError(f'lecture {lecture_id} not found')

            analysis = lecture.get_last_analysis()
            save_message_for_analysis(analysis, 'OpenAI Error', 'GPT-3 Error from OpenAI, it is likely overloaded. Retrying in a little while...')
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
        jobs.gpt_request.job,
        'say hello',
        'ev_wkULk2sk',
        Lecture.Language.SWEDISH,
        ttl=15,
        retry=Retry(max=2, interval=[5, 5]),
    )
    print(j.id)
