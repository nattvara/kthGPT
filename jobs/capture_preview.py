from config.settings import settings
from redis import Redis
from rq import Queue
import logging

from db.crud import get_lecture_by_public_id
from tools.web.camera import save_photo
import jobs.capture_preview


def job(lecture_id: str):
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id(lecture_id)
    url = lecture.content_link()
    logger.info(f'taking photo of {url}')

    save_photo(url, lecture.preview_filename())
    lecture.img_preview = lecture.preview_filename()
    lecture.save()

    logger.info(f'photo saved at {lecture.preview_filename()}')


# Test run the job
if __name__ == '__main__':
    queue = Queue(connection=Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
    ))
    queue.enqueue(jobs.capture_preview.job, '0_3xg3hl0c')
