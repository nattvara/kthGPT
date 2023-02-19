from redis import Redis
from rq import Queue

from db.crud import get_unfinished_analysis, save_message_for_analysis
from config.settings import settings
from db.models.analysis import Analysis
from db.models.lecture import Lecture
from config.logger import log
from jobs import (
    capture_preview,
    download_lecture,
    extract_audio,
    transcribe_audio,
    summarise_transcript,
    classify_video,
)


DEFAULT = 'default'
DOWNLOAD = 'download'
EXTRACT = 'extract'
TRANSCRIBE = 'transcribe'
SUMMARISE = 'summarise'
MONITORING = 'monitoring'
APPROVAL = 'approval'


def get_default_queue() -> Queue:
    try:
        conn = get_connection()
        queue = Queue(DEFAULT, connection=conn)
        yield queue
    finally:
        queue.connection.close()


def get_download_queue() -> Queue:
    try:
        conn = get_connection()
        queue = Queue(DOWNLOAD, connection=conn)
        yield queue
    finally:
        queue.connection.close()


def get_extract_queue() -> Queue:
    try:
        conn = get_connection()
        queue = Queue(EXTRACT, connection=conn)
        yield queue
    finally:
        queue.connection.close()


def get_transcribe_queue() -> Queue:
    try:
        conn = get_connection()
        queue = Queue(TRANSCRIBE, connection=conn)
        yield queue
    finally:
        queue.connection.close()


def get_summarise_queue() -> Queue:
    try:
        conn = get_connection()
        queue = Queue(SUMMARISE, connection=conn)
        yield queue
    finally:
        queue.connection.close()


def get_monitoring_queue() -> Queue:
    try:
        conn = get_connection()
        queue = Queue(MONITORING, connection=conn)
        yield queue
    finally:
        queue.connection.close()


def get_approval_queue() -> Queue:
    try:
        conn = get_connection()
        queue = Queue(APPROVAL, connection=conn)
        yield queue
    finally:
        queue.connection.close()


def get_connection() -> Queue:
    if settings.REDIS_PASSWORD is not None:
        return Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
        )

    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
    )


def schedule_analysis_of_lecture(
    lecture,
    queue_default: Queue = get_default_queue,
    queue_download: Queue = get_download_queue,
    queue_extract: Queue = get_extract_queue,
    queue_transcribe: Queue = get_transcribe_queue,
    queue_summarise: Queue = get_summarise_queue,
):
    if lecture.approved is False:
        log().warning(f'Lecture is not approved, canceling analysis {lecture.public_id}')
        return

    analysis = Analysis(lecture_id=lecture.id)
    analysis.save()

    if lecture.approved is None:
        schedule_approval_of_lecture(lecture)
        return

    log().info(f'Scheduling analysis of {lecture.public_id}')

    save_message_for_analysis(analysis, 'Analysis scheduled', 'Waiting for a worker to pick it up.')

    next(queue_default()).enqueue(capture_preview.job, lecture.public_id, lecture.language, job_timeout=capture_preview.TIMEOUT)
    job_1 = next(queue_download()).enqueue(download_lecture.job, lecture.public_id, lecture.language, job_timeout=download_lecture.TIMEOUT)
    job_2 = next(queue_extract()).enqueue(extract_audio.job, lecture.public_id, lecture.language, job_timeout=extract_audio.TIMEOUT, depends_on=job_1)
    job_3 = next(queue_transcribe()).enqueue(transcribe_audio.job, lecture.public_id, lecture.language, job_timeout=transcribe_audio.TIMEOUT, depends_on=job_2)
    job_4 = next(queue_summarise()).enqueue(summarise_transcript.job, lecture.public_id, lecture.language, job_timeout=summarise_transcript.TIMEOUT, depends_on=job_3)

    return analysis


def schedule_approval_of_lecture(
    lecture,
    queue_approval: Queue = get_approval_queue,
):
    log().info(f'Scheduling approval of {lecture.public_id}')

    next(queue_approval()).enqueue(
        classify_video.job,
        lecture.public_id,
        lecture.language,
        job_timeout=classify_video.TIMEOUT,
    )


def analysis_queues_restart(
    queue_download: Queue = get_download_queue,
    queue_extract: Queue = get_extract_queue,
    queue_transcribe: Queue = get_transcribe_queue,
    queue_summarise: Queue = get_summarise_queue,
):
    analysis = get_unfinished_analysis()

    next(queue_download()).empty()
    next(queue_extract()).empty()
    next(queue_transcribe()).empty()
    next(queue_summarise()).empty()

    lectures = []

    for a in analysis:
        if a.lecture_id not in lectures:
            lectures.append(a.lecture_id)

    for lecture_id in lectures:
        lecture = Lecture.get_by_id(lecture_id)
        schedule_analysis_of_lecture(lecture)
