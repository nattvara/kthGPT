import logging
import os

from db.crud import get_lecture_by_public_id_and_language
from tools.youtube.metadata import get_upload_date
from tools.web.crawler import (
    scrape_posted_date_from_kthplay,
    scrape_title_from_page,
)

# 5 mins
TIMEOUT = 5 * 60


def job(lecture_id: str, language: str):
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id_and_language(lecture_id, language)
    if lecture is None:
        raise ValueError(f'lecture {lecture_id} not found')

    if lecture.source == lecture.Source.KTH:
        logger.info(f'fetching title from {lecture.content_link()}')
        title = scrape_title_from_page(lecture.content_link())
        logger.info(f'fetching title from {lecture.content_link()}')
        date = scrape_posted_date_from_kthplay(lecture.content_link())
    elif lecture.source == lecture.Source.YOUTUBE:
        logger.info(f'fetching title from {lecture.content_link()}')
        title = scrape_title_from_page(lecture.content_link())
        logger.info(f'fetching title from {lecture.content_link()}')
        date = get_upload_date(lecture.content_link())
    elif lecture.source == lecture.Source.KTH_RAW:
        logger.warning('kth_raw does not support metadata')
        return
    else:
        raise ValueError(f'unknown source {lecture.source}')

    lecture.title = title
    lecture.date = date
    lecture.reindex()
    lecture.save()

    logger.info('done.')


# Test run the job
if __name__ == '__main__':
    job('0_bcl3micy', 'en')
