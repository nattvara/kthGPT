from typing import Tuple
import tiktoken
import openai

from config.settings import settings
from db.models import TokenUsage


MODEL = 'text-davinci-003'


class TokenLimitExceededException(Exception):
    pass


class UnexpectedOpenAIException(Exception):
    pass


def get_max_tokens(prompt: str) -> int:
    encoder = tiktoken.encoding_for_model(MODEL)
    return 4000 - len(encoder.encode(prompt))


def completion(prompt: str) -> Tuple[str, TokenUsage]:
    tokens = get_max_tokens(prompt)
    if tokens < 0:
        raise TokenLimitExceededException(f'to many tokens ({tokens})')

    openai.api_key = settings.OPENAI_API_KEY
    try:
        completion = openai.Completion.create(
            engine=MODEL,
            prompt=prompt,
            max_tokens=get_max_tokens(prompt),
        )
    except Exception as e:
        raise UnexpectedOpenAIException(e)

    usage = TokenUsage(
        completion_tokens=completion['usage']['completion_tokens'],
        prompt_tokens=completion['usage']['prompt_tokens'],
        total_tokens=completion['usage']['total_tokens'],
    )
    return completion['choices'][0]['text'].strip(), usage
