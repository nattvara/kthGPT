from openai.error import RateLimitError
from redis import Redis
from rq import Queue
import logging

from tools.text.openai import completion
from config.settings import settings
import jobs.gpt_request


def job(prompt: str):
    logger = logging.getLogger('rq.worker')
    response = completion(prompt)
    return response


# Test run the job
if __name__ == '__main__':
    queue = Queue('gpt', connection=Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
    ))
    j = queue.enqueue(jobs.gpt_request.job, 'say hello')
    print(j.id)
