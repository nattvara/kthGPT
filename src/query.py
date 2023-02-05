from revChatGPT.Official import AsyncChatbot
from lecture import Lecture
import asyncio


async def ask_async_wrapper(text: str, api_key: str) -> str:
    bot = AsyncChatbot(api_key=api_key)
    res = await bot.ask(text)
    return res['choices'][0]['text']


def ask(lecture: Lecture, question: str, api_key: str) -> str:
    prompt = f'''
The following is a summary of a recorded lecture
------------------------------------------------
{lecture.summary_text}

------------------------------------------------
Now answer the following query: {question}
    '''.strip()

    return asyncio.run(ask_async_wrapper(prompt, api_key))
