import logging

from db.models import Analysis
from db.crud import (
    delete_all_except_last_message_in_analysis,
    get_lecture_by_public_id_and_language,
    get_all_analysis_for_lecture,
)


def job(lecture_id: str, language: str):
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id_and_language(lecture_id, language)
    if lecture is None:
        raise ValueError(f'lecture {lecture_id} not found')

    if lecture.get_last_analysis().state != Analysis.State.READY:
        logger.error(f'can only clean lectures with ready state, lecture had state {lecture.get_last_analysis().state}')  # noqa: E501
        return

    for analysis in get_all_analysis_for_lecture(lecture.id):
        delete_all_except_last_message_in_analysis(analysis.id)
    logger.info('done.')


# Test run the job
if __name__ == '__main__':
    job('0_pkrd51s7', 'en')
