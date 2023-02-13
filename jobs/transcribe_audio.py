from config.settings import settings
from redis import Redis
from rq import Queue
import logging

from db.crud import get_lecture_by_public_id_and_language
from tools.audio.transcription import save_text
from db.models import Lecture, Analysis
import jobs.transcribe_audio


# 2hr timeout
TIMEOUT = 2 * 60 * 60


def job(lecture_id: str, language: str):
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id_and_language(lecture_id, language)
    if lecture is None:
        raise ValueError(f'lecture {lecture_id} not found')

    lecture.refresh()
    analysis = lecture.get_last_analysis()
    analysis.state = Analysis.State.TRANSCRIBING_LECTURE
    analysis.save()

    try:
        if lecture.mp3_filepath is None:
            raise ValueError(f'lecture {lecture_id} has no mp3_filepath')

        logger.info(f'transcribing {lecture.mp3_filepath}')

        save_text(lecture.mp3_filepath, lecture)

        lecture.refresh()
        lecture.words = lecture.count_words()
        lecture.save()

        analysis = lecture.get_last_analysis()
        analysis.transcript_progress = 100
        analysis.state = Analysis.State.IDLE
        analysis.save()
        logger.info('done')

    except Exception as e:
        logger.error(e)

        lecture.refresh()
        analysis = lecture.get_last_analysis()
        analysis.state = Analysis.State.FAILURE
        analysis.save()
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
        '0_blzql89t',
        Lecture.Language.ENGLISH,
        job_timeout=TIMEOUT
    )
