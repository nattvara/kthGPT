from config.settings import settings
from redis import Redis
from rq import Queue
import logging

from tools.web.downloader import download_mp4_from_m3u8
from tools.youtube.download import download_mp4
from db.models import Lecture, Analysis
import jobs.pipelines.analyse_lecture.download_lecture
import jobs.tasks.lecture.capture_preview
import tools.web.crawler as crawler
from db.crud import (
    get_lecture_by_public_id_and_language,
    save_message_for_analysis
)


# 20min timeout
TIMEOUT = 20 * 60


def download_mp4_from_kthplay(lecture: Lecture):
    logger = logging.getLogger('rq.worker')

    url = lecture.content_link()
    lecture.refresh()
    analysis = lecture.get_last_analysis()
    analysis.mp4_progress = 2
    analysis.save()

    logger.info(f'fetching content link at {url}')
    save_message_for_analysis(analysis, 'Downloading...', 'Looking for link to content.')
    m3u8_url = crawler.get_m3u8(url)
    logger.info(f'found {m3u8_url}')

    lecture.refresh()
    analysis.mp4_progress = 3
    analysis.save()

    save_message_for_analysis(analysis, 'Downloading...', 'Retrieving the recorded lecture, this is usually pretty quick.')
    download_mp4_from_m3u8(m3u8_url, lecture)


def download_mp4_from_youtube(lecture: Lecture):
    url = lecture.content_link()

    lecture.refresh()
    analysis = lecture.get_last_analysis()
    analysis.mp4_progress = 50
    analysis.save()

    save_message_for_analysis(analysis, 'Downloading...', 'Downloading the video from youtube.')
    download_mp4(url, lecture)


def job(lecture_id: str, language: str):
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id_and_language(lecture_id, language)
    if lecture is None:
        raise ValueError(f'lecture {lecture_id} not found')

    lecture.refresh()
    analysis = lecture.get_last_analysis()
    analysis.state = Analysis.State.DOWNLOADING
    analysis.mp4_progress = 1
    analysis.save()

    try:
        if lecture.source == Lecture.Source.KTH:
            download_mp4_from_kthplay(lecture)
        elif lecture.source == Lecture.Source.YOUTUBE:
            download_mp4_from_youtube(lecture)
        elif lecture.source == Lecture.Source.KTH_RAW:
            download_mp4_from_m3u8(lecture.raw_content_link, lecture)
        else:
            raise ValueError(f'unsupported lecture source {lecture.source}')

        lecture.refresh()
        analysis = lecture.get_last_analysis()
        analysis.state = Analysis.State.IDLE
        analysis.mp4_progress = 100
        analysis.save()
        save_message_for_analysis(analysis, 'Downloaded', 'The video has been downloaded, waiting for audio extraction to start.')  # noqa: E501

        logger.info('queueing extraction job')
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
        jobs.pipelines.analyse_lecture.download_lecture.job,
        'mn9LOFQc9IE',
        Lecture.Language.SWEDISH
    )
