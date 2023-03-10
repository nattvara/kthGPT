from rq import Queue

from db.crud import (
    get_all_ready_lectures,
    get_all_lectures,
)
from jobs import (
    schedule_analysis_of_lecture,
    schedule_cleanup_of_lecture,
    get_metadata_queue,
    capture_preview,
    fetch_metadata,
)


def fetch_metadata_for_all_lectures(
    queue_metadata: Queue = get_metadata_queue,
):
    print('dispatching jobs to fetch metadata for all lectures')
    lectures = get_all_lectures()

    print(f'number of lectures: {len(lectures)}')

    q = next(queue_metadata())
    for lecture in lectures:
        q.enqueue(
            fetch_metadata.job,
            lecture.public_id,
            lecture.language,
            job_timeout=fetch_metadata.TIMEOUT,
        )


def capture_preview_for_all_lectures(
    queue_metadata: Queue = get_metadata_queue,
):
    print('dispatching jobs to capture preview for all lectures')
    lectures = get_all_lectures()

    print(f'number of lectures: {len(lectures)}')

    q = next(queue_metadata())
    for lecture in lectures:
        q.enqueue(
            capture_preview.job,
            lecture.public_id,
            lecture.language,
            job_timeout=capture_preview.TIMEOUT,
        )


def cleanup_for_all_lectures():
    print('dispatching jobs to do cleanup on all lectures')

    lectures = get_all_ready_lectures()
    for lecture in lectures:
        print(f'scheduling clean of {lecture.id}')
        schedule_cleanup_of_lecture(lecture)


def reanalyse_all_lectures():
    print('dispatching jobs to re-analyse all lectures')

    lectures = get_all_ready_lectures()
    for lecture in lectures:
        print(f'scheduling analysis of {lecture.id}')
        schedule_analysis_of_lecture(lecture)
