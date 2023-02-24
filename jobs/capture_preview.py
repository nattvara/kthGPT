from config.settings import settings
from redis import Redis
from rq import Queue
import logging

from db.crud import get_lecture_by_public_id_and_language
from tools.web.camera import save_photo
from db.models import Lecture
import jobs.capture_preview

# 5min timeout
TIMEOUT = 5 * 60


def job(lecture_id: str, language: str):
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id_and_language(lecture_id, language)
    url = lecture.content_link()
    logger.info(f'taking photo of {url}')

    save_photo(url, lecture)
    lecture.refresh()
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
    queue.enqueue(
        jobs.capture_preview.job,
        'vJtpKwOKpOM',
        Lecture.Language.SWEDISH
    )
