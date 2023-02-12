from openai.error import RateLimitError
import tiktoken
import logging
import openai
import time

from config.settings import settings

MODEL = 'text-davinci-003'


class RetryLimitException(Exception):
    pass


class TokenLimitExceededException(Exception):
    pass


def get_max_tokens(prompt: str) -> int:
    encoder = tiktoken.encoding_for_model(MODEL)
    return 4000 - len(encoder.encode(prompt))


def gpt3(prompt: str, retry_limit=10) -> str:
    if retry_limit <= 0:
        raise RetryLimitException('reached retry limit')

    tokens = get_max_tokens(prompt)
    if tokens < 0:
        raise TokenLimitExceededException(f'too many tokens ({tokens})')

    openai.api_key = settings.OPENAI_API_KEY
    completion = openai.Completion.create(
        engine=MODEL,
        prompt=prompt,
        max_tokens=get_max_tokens(prompt),
    )

    return completion['choices'][0]['text'].strip()


def gpt3_safe(prompt: str, retry_limit=10) -> str:
    logger = logging.getLogger('rq.worker')

    if retry_limit <= 0:
        raise RetryLimitException('reached retry limit')

    tokens = get_max_tokens(prompt)
    if tokens < 0:
        raise TokenLimitExceededException(f'too many tokens ({tokens})')

    openai.api_key = settings.OPENAI_API_KEY
    try:
        completion = openai.Completion.create(
            engine=MODEL,
            prompt=prompt,
            max_tokens=get_max_tokens(prompt),
        )
    except RateLimitError:
        logger.warning('hit rate limit, waiting 10s')
        time.sleep(10)
        return gpt3_safe(prompt, retry_limit=retry_limit-1)
    except Exception as e:
        logger.error('got an unexpected error, waiting 60s')
        logger.error(e)
        time.sleep(60)
        return gpt3_safe(prompt, retry_limit=retry_limit-1)

    return completion['choices'][0]['text'].strip()
