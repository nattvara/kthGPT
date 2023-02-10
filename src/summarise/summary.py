from revChatGPT.Official import AsyncChatbot
import asyncio
import time
import math


def seconds_to_time(seconds):
    minutes = math.floor(seconds // 60)
    remainder = math.floor(seconds % 60)
    time = f'{minutes:02}:{remainder:02}'
    return time


class Chunk:

    def __init__(self, text: str, start: int, end: int) -> None:
        self.text = text
        self.start = start
        self.end = end

    def to_string(self) -> str:
        return f'[{seconds_to_time(self.start)}-{seconds_to_time(self.end)}] {self.text}'


async def ask_async_wrapper(text: str, api_key: str) -> str:
    bot = AsyncChatbot(api_key=api_key)
    res = await bot.ask(text)
    return res['choices'][0]['text']


def ask(text: str, api_key: str) -> str:
    return asyncio.run(ask_async_wrapper(text, api_key))


def create_summary(chunks: list, chunk_size: int, api_key: str) -> str:
    current_summary = f'''
The following is the current summarised content of a recorded lecture:

00:00 - 00:00
- Lecture starts
    '''.strip()

    for chunk in chunks:
        chunk_time = chunk[0]
        chunk_transcript = chunk[1]

        prompt = f'''
{current_summary}

Here is a transcript of the next {chunk_size} minutes, could you summarise this part of the transcript into 250 words, try to include all important keywords:
{chunk_transcript}
        '''.strip()

        got_reply = False
        limit = 10
        inc = 0
        while not got_reply and inc < limit:
            try:
                response = ask(prompt, api_key)
                got_reply = True
            except Exception as e:
                print(e)
                print(f'{inc + 1}/{limit} failed to get a reply from chatGPT, retrying in 60s...')
                time.sleep(60)
                inc += 1

        if not got_reply:
            raise Exception('failed to reach chatGPT')

        current_summary += f'''

{chunk_time}
{response}
'''

    return current_summary


def create_chunks(segments: list, min_size: int) -> list:
    end = segments[len(segments) - 1]['end']

    no_chunks = math.ceil(end / 60 / min_size)

    chunk_steps = list(range(0, no_chunks * min_size, min_size))
    chunk_data = list(range(0, no_chunks * min_size, min_size))
    for idx, _ in enumerate(chunk_data):
        chunk_data[idx] = []

    for idx, current_chunk in enumerate(chunk_steps):
        if idx >= len(chunk_steps) - 1:
            next_chunk = current_chunk + 10
        else:
            next_chunk = chunk_steps[idx+1]

        for segment in segments:
            segment_min = segment['end'] / 60

            if segment_min >= current_chunk and segment_min < next_chunk:
                chunk_data[idx].append(Chunk(
                    segment['text'],
                    segment['start'],
                    segment['end'],
                ))

    chunked_transcript = []
    for idx, chunks in enumerate(chunk_data):
        current_chunk = chunk_steps[idx]
        if idx >= len(chunk_steps) - 1:
            next_chunk = current_chunk + 10
        else:
            next_chunk = chunk_steps[idx+1]

        chunk_time = f'Transcript between {current_chunk}:00 and {next_chunk}:00 have been summarised to:'

        chunk_transcript = ''
        for chunk in chunks:
            chunk_transcript += chunk.to_string()
            chunk_transcript += '\n'

        chunked_transcript.append([chunk_time, chunk_transcript])

    return chunked_transcript
