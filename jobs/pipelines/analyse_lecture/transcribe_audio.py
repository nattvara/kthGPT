import logging

from db.crud import get_lecture_by_public_id_and_language, save_message_for_analysis
from tools.audio.transcription import save_text
from db.models import Lecture, Analysis


# 5hr timeout
TIMEOUT = 5 * 60 * 60


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
        save_message_for_analysis(analysis, 'Creating transcript...', 'This is going to take a while.')

        save_text(lecture.mp3_filepath, lecture)

        lecture.refresh()
        lecture.words = lecture.count_words()
        lecture.save()

        analysis = lecture.get_last_analysis()
        analysis.transcript_progress = 100
        analysis.state = Analysis.State.IDLE
        analysis.save()
        save_message_for_analysis(analysis, 'Transcribed', 'The lecture has been transcribed, waiting for summary to start.')

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
    job('0_hjbdw7nf', Lecture.Language.SWEDISH)
