from config.settings import settings
from redis import Redis
from rq import Queue
import logging

from db.crud import get_lecture_by_public_id_and_language, save_message_for_analysis
from tools.audio.extraction import extract_mp3_from_mp4
from db.models import Lecture, Analysis
import jobs.extract_audio


# 20min timeout
TIMEOUT = 20 * 60


def job(lecture_id: str, language: str):
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id_and_language(lecture_id, language)
    if lecture is None:
        raise ValueError(f'lecture {lecture_id} not found')

    lecture.refresh()
    analysis = lecture.get_last_analysis()
    analysis.state = Analysis.State.EXTRACTING_AUDIO
    analysis.save()

    try:
        if lecture.mp4_filepath is None:
            raise ValueError(f'lecture {lecture_id} has no mp4_filepath')

        save_message_for_analysis(analysis, 'Extracting audio...', 'The analyzer only looks at what is being said in the lecture.')
        logger.info(f'extracting audio from {lecture.mp4_filepath}')
        extract_mp3_from_mp4(lecture.mp4_filepath, lecture)

        lecture.refresh()
        analysis = lecture.get_last_analysis()
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
    queue.enqueue(jobs.extract_audio.job, '0_blzql89t', Lecture.Language.ENGLISH)
