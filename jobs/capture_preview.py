from config.settings import settings
from redis import Redis
from rq import Queue
import logging

from db.crud import get_lecture_by_public_id_and_language
from tools.video.img import save_photo_from_video
from tools.web.camera import save_photo
from db.models import Lecture
import jobs.capture_preview

# 5min timeout
TIMEOUT = 5 * 60


def job(lecture_id: str, language: str):
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id_and_language(lecture_id, language)
    if lecture.raw_content_link is not None:
        logger.info(f'content has raw link, using mp4 file')
        if lecture.mp4_filepath is None:
            raise ValueError('mp4_filepath was not specified')

        mp4 = lecture.mp4_filepath
        save_photo_from_video(mp4, lecture.preview_filename())
        save_photo_from_video(mp4, lecture.preview_small_filename(), True)

        lecture.refresh()
        lecture.img_preview = lecture.preview_filename()
        lecture.img_preview_small = lecture.preview_small_filename()
        lecture.save()
        return

    url = lecture.content_link()
    logger.info(f'taking photo of {url}')

    save_photo(url, lecture)
    logger.info(f'photo saved at {lecture.preview_filename()}')

    save_photo(url, lecture, small=True)
    logger.info(f'photo saved at {lecture.preview_small_filename()}')

    lecture.refresh()
    lecture.img_preview = lecture.preview_filename()
    lecture.img_preview_small = lecture.preview_small_filename()
    lecture.save()



# Test run the job
if __name__ == '__main__':
    queue = Queue(connection=Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
    ))
    queue.enqueue(
        jobs.capture_preview.job,
        '0_hdz62g82',
        Lecture.Language.SWEDISH
    )
