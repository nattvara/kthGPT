from redis import Redis
from rq import Queue

from db.crud import (
    get_unfinished_lectures,
    save_message_for_analysis,
)
from db.models.analysis import Analysis
from jobs.pipelines.analyse_lecture import (
    download_lecture,
    extract_audio,
    summarise_transcript,
    transcribe_audio,
)
from config.settings import settings
from jobs.tasks.lecture import (
    capture_preview,
    classify_video,
    clean_lecture,
    index_lecture
)
from jobs.tasks.lecture import (
    fetch_metadata,
)
from config.logger import log


DEFAULT = 'default'
DOWNLOAD = 'download'
EXTRACT = 'extract'
TRANSCRIBE = 'transcribe'
SUMMARISE = 'summarise'
MONITORING = 'monitoring'
APPROVAL = 'approval'
GPT = 'gpt'
METADATA = 'metadata'


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


def get_metadata_queue() -> Queue:
    try:
        conn = get_connection()
        queue = Queue(METADATA, connection=conn)
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
    queue_metadata: Queue = get_metadata_queue,
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

    # analysis sequence
    download = next(queue_download()).enqueue(download_lecture.job, lecture.public_id, lecture.language, job_timeout=download_lecture.TIMEOUT)  # noqa: E501
    extract = next(queue_extract()).enqueue(extract_audio.job, lecture.public_id, lecture.language, job_timeout=extract_audio.TIMEOUT, depends_on=download)  # noqa: E501
    transcribe = next(queue_transcribe()).enqueue(transcribe_audio.job, lecture.public_id, lecture.language, job_timeout=transcribe_audio.TIMEOUT, depends_on=extract)  # noqa: E501
    summarise = next(queue_summarise()).enqueue(summarise_transcript.job, lecture.public_id, lecture.language, job_timeout=summarise_transcript.TIMEOUT, depends_on=transcribe)  # noqa: E501

    # other jobs that depend on different steps in the analysis
    metadata = next(get_metadata_queue()).enqueue(fetch_metadata.job, lecture.public_id, lecture.language, job_timeout=fetch_metadata.TIMEOUT)  # noqa: F841, E501
    preview = next(queue_metadata()).enqueue(capture_preview.job, lecture.public_id, lecture.language, job_timeout=capture_preview.TIMEOUT, depends_on=download)  # noqa: F841, E501
    clean = next(queue_metadata()).enqueue(clean_lecture.job, lecture.public_id, lecture.language, depends_on=summarise)  # noqa: F841, E501
    index = next(queue_metadata()).enqueue(index_lecture.job, lecture.public_id, lecture.language, depends_on=summarise)  # noqa: F841, E501

    return analysis


def schedule_fetch_of_lecture_metadata(
    lecture,
    queue_metadata: Queue = get_metadata_queue,
):
    log().info(f'Scheduling fetch of metadata for {lecture.public_id}')

    next(queue_metadata()).enqueue(
        fetch_metadata.job,
        lecture.public_id,
        lecture.language,
        job_timeout=fetch_metadata.TIMEOUT,
    )


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


def schedule_cleanup_of_lecture(
    lecture,
    queue_metadata: Queue = get_metadata_queue,
):
    log().info(f'Scheduling cleanup of {lecture.public_id}')

    next(queue_metadata()).enqueue(
        clean_lecture.job,
        lecture.public_id,
        lecture.language,
    )


def analysis_queues_restart(
    queue_download: Queue = get_download_queue,
    queue_extract: Queue = get_extract_queue,
    queue_transcribe: Queue = get_transcribe_queue,
    queue_summarise: Queue = get_summarise_queue,
):
    next(queue_download()).empty()
    next(queue_extract()).empty()
    next(queue_transcribe()).empty()
    next(queue_summarise()).empty()

    lectures = get_unfinished_lectures()
    for lecture in lectures:
        print(f'scheduling re-analysis of lecture {lecture.id}')
        schedule_analysis_of_lecture(lecture)
