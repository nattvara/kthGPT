from config.settings import settings
from redis import Redis
from rq import Queue
import logging

from tools.web.downloader import download_mp4_from_m3u8
from db.crud import get_lecture_by_public_id
from tools.audio.extraction import extract_mp3_from_mp4
from db.models import Lecture
import jobs.extract_audio


def job(lecture_id: str):
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id(lecture_id)
    if lecture is None:
        raise ValueError(f'lecture {lecture_id} not found')

    lecture.state = Lecture.State.EXTRACTING_AUDIO
    lecture.save()

    try:
        if lecture.mp4_filepath is None:
            raise ValueError(f'lecture {lecture_id} has no mp4_filepath')

        logger.info(f'extracting audio from {lecture.mp4_filepath}')
        extract_mp3_from_mp4(lecture.mp4_filepath, lecture)

        lecture.state = Lecture.State.IDLE
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
    queue.enqueue(jobs.extract_audio.job, '0_3xg3hl0c')
