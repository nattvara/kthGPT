from config.settings import settings
from redis import Redis
from rq import Queue

from db.crud import get_lecture_by_public_id_and_language
from db.models import Lecture
import jobs.capture_preview
import tools.video.img

# 5min timeout
TIMEOUT = 5 * 60


def job(lecture_id: str, language: str):
    lecture = get_lecture_by_public_id_and_language(lecture_id, language)

    if lecture.mp4_filepath is None:
        raise ValueError('mp4_filepath was not specified')

    mp4 = lecture.mp4_filepath
    tools.video.img.save_photo_from_video(mp4, lecture.preview_filename())
    tools.video.img.save_photo_from_video(mp4, lecture.preview_small_filename(), True)

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
