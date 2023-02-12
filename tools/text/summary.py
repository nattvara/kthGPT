import logging
import math

from . import prompts, ai
from db.models import Lecture


class Chunk:

    def __init__(self, period: str, transcript: str) -> None:
        self.period = period
        self.transcript = transcript

    @staticmethod
    def create_chunks(segments: list, min_size: int) -> list:
        def minutes_to_time(minutes):
            hours = math.floor(minutes // 60)
            remainder = math.floor(minutes % 60)
            time = f'{hours:02}:{remainder:02}:00'
            return time

        end = segments[len(segments) - 1]['end']

        number_of_chunks = math.ceil(end / 60 / min_size)

        chunk_steps = list(range(0, number_of_chunks * min_size, min_size))
        chunk_data = list(range(0, number_of_chunks * min_size, min_size))
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
                    chunk_data[idx].append(segment['text'])

        chunked_transcript = []
        for idx, chunks in enumerate(chunk_data):
            current_chunk = chunk_steps[idx]
            if idx >= len(chunk_steps) - 1:
                next_chunk = current_chunk + 10
            else:
                next_chunk = chunk_steps[idx+1]

            chunk_time = f'{minutes_to_time(current_chunk)} - {minutes_to_time(next_chunk)}'

            chunk_transcript = ''
            for chunk in chunks:
                chunk_transcript += chunk
                chunk_transcript += '\n'

            chunked_transcript.append(Chunk(chunk_time, chunk_transcript))

        return chunked_transcript


class Summary:

    def __init__(self, min_size: int, summary_size: int) -> None:
        self.min_size = min_size
        self.summary_size = summary_size
        self.summaries = {
        }

    def update_with_chunk(self, chunk: Chunk, include_summary: bool):
        prompt = prompts.create_text_to_summarise_chunk(self, chunk, include_summary)
        response = ai.gpt3_safe(prompt)
        self.summaries[chunk.period] = response.replace('\n', ' ')

    def current_summary(self):
        string = ''
        for period in self.summaries:
            summary = self.summaries[period]
            string += f'{period}: {summary}\n'
        return string

    def summarise(self):
        prompt = prompts.create_text_to_summarise_summary(self)
        response = ai.gpt3_safe(prompt)
        return response

    @staticmethod
    def create_summary(lecture: Lecture, min_size):
        logger = logging.getLogger('rq.worker')

        segments = lecture.get_segments()
        chunks = Chunk.create_chunks(segments, min_size)
        summary = Summary(min_size, 50)

        try:
            include_summary = False

            inc = 0
            for chunk in chunks:
                inc += 1
                summary.update_with_chunk(chunk, include_summary)
                include_summary = True

                progress = int((inc / len(chunks)) * 100)
                logger.info(f'current progress {progress}%')

                lecture.summary_progress = progress
                lecture.save()

        except ai.TokenLimitExceededException:
            new_min_size = min_size * 2
            return Summary.create_summary(segments, new_min_size)

        return summary
