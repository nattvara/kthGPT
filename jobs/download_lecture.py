from config.settings import settings
from redis import Redis
from rq import Queue
import logging

from tools.web.downloader import download_mp4_from_m3u8
from db.crud import get_lecture_by_public_id
from tools.web.crawler import get_m3u8
from db.models import Lecture
import jobs.download_lecture
import jobs.extract_audio


def job(lecture_id: str):
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id(lecture_id)
    if lecture is None:
        raise ValueError(f'lecture {lecture_id} not found')

    lecture.state = Lecture.State.DOWNLOADING
    lecture.save()

    try:
        url = lecture.content_link()

        logger.info(f'fetching content link at {url}')
        m3u8_url = get_m3u8(url)
        logger.info(f'found {m3u8_url}')
        download_mp4_from_m3u8(m3u8_url, lecture)

        lecture.state = Lecture.State.IDLE
        lecture.save()

        logger.info('queueing extraction job')
        queue = Queue(connection=Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
        ))
        queue.enqueue(jobs.extract_audio.job, lecture.public_id)
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
    queue.enqueue(jobs.download_lecture.job, '0_3xg3hl0c')
