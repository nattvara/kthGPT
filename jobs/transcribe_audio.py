from config.settings import settings
from redis import Redis
from rq import Queue
import logging

from db.crud import get_lecture_by_public_id_and_language
from tools.audio.transcription import save_text
from db.models import Lecture
import jobs.transcribe_audio


# 2hr timeout
TIMEOUT = 2 * 60 * 60


def job(lecture_id: str, language: str):
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id_and_language(lecture_id, language)
    if lecture is None:
        raise ValueError(f'lecture {lecture_id} not found')

    lecture.refresh()
    lecture.state = Lecture.State.TRANSCRIBING_LECTURE
    lecture.save()

    try:
        if lecture.mp3_filepath is None:
            raise ValueError(f'lecture {lecture_id} has no mp3_filepath')

        logger.info(f'transcribing {lecture.mp3_filepath}')

        save_text(lecture.mp3_filepath, lecture)

        lecture.refresh()
        lecture.words = lecture.count_words()
        lecture.state = Lecture.State.IDLE
        lecture.save()
        logger.info('done')

    except Exception as e:
        lecture.refresh()
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
        jobs.transcribe_audio.job,
        '0_a9vo7yd0',
        Lecture.Language.SWEDISH,
        job_timeout=TIMEOUT
    )
