from rq import Queue

from db.crud import get_all_lectures
from jobs import (
    get_metadata_queue,
    fetch_metadata
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
