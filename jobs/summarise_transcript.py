from config.settings import settings
from redis import Redis
from rq import Queue
import logging
import os

from db.crud import get_lecture_by_public_id_and_language, save_message_for_analysis
from db.models import Lecture, Analysis
import jobs.summarise_transcript


# 90min timeout
TIMEOUT = 90 * 60


def job(lecture_id: str, language: str):
    from tools.text.summary import Summary
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id_and_language(lecture_id, language)
    if lecture is None:
        raise ValueError(f'lecture {lecture_id} not found')

    lecture.refresh()
    analysis = lecture.get_last_analysis()
    analysis.state = Analysis.State.SUMMARISING_LECTURE
    analysis.save()

    try:
        if lecture.mp3_filepath is None:
            raise ValueError(f'lecture {lecture_id} has no mp3_filepath')

        logger.info(f'summarising {lecture.transcript_filepath}')

        save_message_for_analysis(analysis, 'Creating summary...', 'Summarizing the lecture into something you can query.')

        min_size = round((lecture.length / 60) / 22)
        if min_size < 2:
            min_size = 2

        logger.info(f'using minute size {min_size}')

        summary = Summary.create_summary(lecture, min_size)

        output_filename = lecture.summary_filename()
        if os.path.isfile(output_filename):
            os.unlink(output_filename)

        with open(output_filename, 'w+') as file:
            file.write(summary.current_summary())

        lecture.refresh()
        lecture.summary_filepath = output_filename
        lecture.save()

        analysis = lecture.get_last_analysis()
        analysis.summary_progress = 100
        analysis.state = Analysis.State.READY
        analysis.save()

        save_message_for_analysis(analysis, 'Done!', 'kthGPT has finished watching the lecture.')

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
        jobs.summarise_transcript.job,
        'rVzDRfO2sgs',
        Lecture.Language.ENGLISH,
        job_timeout=TIMEOUT
    )
