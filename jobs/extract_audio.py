from config.settings import settings
from redis import Redis
from rq import Queue
import logging

from db.crud import get_lecture_by_public_id_and_language
from tools.audio.extraction import extract_mp3_from_mp4
from db.models import Lecture
import jobs.extract_audio


# 20min timeout
TIMEOUT = 20 * 60


def job(lecture_id: str, language: str):
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id_and_language(lecture_id, language)
    if lecture is None:
        raise ValueError(f'lecture {lecture_id} not found')

    lecture.refresh()
    lecture.state = Lecture.State.EXTRACTING_AUDIO
    lecture.save()

    try:
        if lecture.mp4_filepath is None:
            raise ValueError(f'lecture {lecture_id} has no mp4_filepath')

        logger.info(f'extracting audio from {lecture.mp4_filepath}')
        extract_mp3_from_mp4(lecture.mp4_filepath, lecture)

        lecture.refresh()
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
    queue.enqueue(jobs.extract_audio.job, '0_3xg3hl0c', Lecture.Language.ENGLISH)
