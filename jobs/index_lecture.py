import logging

from db.crud import get_lecture_by_public_id_and_language
import index.lecture as lecture_index

def job(lecture_id: str, language: str):
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id_and_language(lecture_id, language)
    if lecture is None:
        raise ValueError(f'lecture {lecture_id} not found')

    lecture_index.index(lecture)

    logger.info('done.')


# Test run the job
if __name__ == '__main__':
    # Should be queued on a save of the lecture
    lecture_id = '0_bcl3micy'
    language = 'en'
    lecture = get_lecture_by_public_id_and_language(lecture_id, language)
    if lecture is None:
        raise ValueError(f'lecture {lecture_id} not found')

    lecture.save()
