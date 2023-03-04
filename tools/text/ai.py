from datetime import datetime, timedelta
from openai.error import RateLimitError
from typing import Optional
from rq import Queue, Retry
from redis import Redis
from rq.job import Job
import tiktoken
import asyncio

from config.settings import settings
from config.logger import log
import jobs.gpt_request


MODEL = 'text-davinci-003'

GPT_QUEUE_NAME = 'gpt'

POLLING_INTERVAL_SECONDS = 0.1


class GPTException(Exception):
    pass


class RetryLimitException(Exception):
    pass


class TokenLimitExceededException(Exception):
    pass


class JobResponseErrorException(Exception):
    pass


class JobTimeoutException(Exception):
    pass


def get_gpt_queue() -> Queue:
    try:
        conn = get_connection()
        queue = Queue(GPT_QUEUE_NAME, connection=conn)
        yield queue
    finally:
        queue.connection.close()


def get_connection() -> Queue:
    if settings.REDIS_PASSWORD is not None:
        return Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
        )

    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
    )


def get_max_tokens(prompt: str) -> int:
    encoder = tiktoken.encoding_for_model(MODEL)
    return 4000 - len(encoder.encode(prompt))


def gpt3(
    prompt: str,
    time_to_live: int = 60,
    max_retries: int = 3,
    retry_interval: list = [10, 30, 60],
    queue_approval: Queue = get_gpt_queue,
    analysis_id: Optional[int] = None,
    query_id: Optional[int] = None,
) -> str:
    q = next(queue_approval())

    job = q.enqueue(
        jobs.gpt_request.job,
        prompt,
        analysis_id,
        query_id,
        ttl=time_to_live,
        retry=Retry(max=max_retries, interval=retry_interval)
    )

    try:
        response = asyncio.run(wait_for_response(
            job.id,
            get_connection(),
            time_to_live,
        ))
        return response
    except JobResponseErrorException as e:
        log().error(e)
        raise GPTException('GPT-3 Error. OpenAI failed, it is likely overloaded.')
    except JobTimeoutException as e:
        log().error(e)
        raise GPTException('GPT-3 Error. OpenAI took too long, it is likely overloaded.')
    except RateLimitError as e:
        log().error(e)
        raise GPTException('GPT-3 Rate limit. kthGPT is overloaded.')


async def wait_for_response(job_id: str, connection: Queue, trigger_timout_after: int) -> str:
    timeout_after = datetime.utcnow() + timedelta(seconds=trigger_timout_after)

    job = Job.fetch(job_id, connection=connection)

    while True:
        job.refresh()

        now = datetime.utcnow()
        if now > timeout_after:
            raise JobTimeoutException(f'reached job timeout limit of {trigger_timout_after}')

        status = job.get_status()
        if status == 'finished':
            return job.result

        error_statuses = [
            'stopped',
            'canceled',
            'failed',
        ]
        if status in error_statuses:
            # Some messy error handling here since the error
            # info is sent back as a string from rq

            rate_limit = (RateLimitError()).__class__.__name__
            if rate_limit in str(job.exc_info):
                raise RateLimitError()

            raise JobResponseErrorException(f'job failed with error {status}')

        await asyncio.sleep(POLLING_INTERVAL_SECONDS)
