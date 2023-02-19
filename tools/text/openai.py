import tiktoken
import openai

from config.settings import settings


MODEL = 'text-davinci-003'


class TokenLimitExceededException(Exception):
    pass


class UnexpectedOpenAIException(Exception):
    pass


def get_max_tokens(prompt: str) -> int:
    encoder = tiktoken.encoding_for_model(MODEL)
    return 4000 - len(encoder.encode(prompt))


def completion(prompt: str) -> str:
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

    return completion['choices'][0]['text'].strip()
