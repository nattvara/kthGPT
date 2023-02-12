from config.settings import settings
from redis import Redis
from rq import Queue
import logging
import os

from db.crud import get_lecture_by_public_id_and_language
from tools.text.summary import Summary
from db.models import Lecture
import jobs.summarise_transcript


# 90min timeout
SUMMARY_JOB_TIMEOUT = 60 * 90


def job(lecture_id: str, language: str):
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id_and_language(lecture_id, language)
    if lecture is None:
        raise ValueError(f'lecture {lecture_id} not found')

    lecture.state = Lecture.State.SUMMARISING_LECTURE
    lecture.save()

    try:
        if lecture.mp3_filepath is None:
            raise ValueError(f'lecture {lecture_id} has no mp3_filepath')

        logger.info(f'summarising {lecture.transcript_filepath}')

        min_size = round((lecture.length / 60) / 25)
        if min_size == 0:
            min_size = 1

        logger.info(f'using minute size {min_size}')

        summary = Summary.create_summary(lecture, min_size)

        output_filename = lecture.summary_filename()
        if os.path.isfile(output_filename):
            os.unlink(output_filename)

        with open(output_filename, 'w+') as file:
            file.write(summary.current_summary())

        lecture.summary_filepath = output_filename
        lecture.summary_progress = 100
        lecture.save()

        lecture.state = Lecture.State.READY
        lecture.save()
        logger.info('done')

    except Exception as e:
        lecture.state = Lecture.State.FAILURE
        lecture.save()
        raise e


# Test run the job
if __name__ == '__main__':
    queue = Queue(connection=Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
    ))
    queue.enqueue(
        jobs.summarise_transcript.job,
        '0_u40du3a9',
        Lecture.Language.ENGLISH,
        job_timeout=SUMMARY_JOB_TIMEOUT
    )
