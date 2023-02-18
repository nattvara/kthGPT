from redis import Redis
from rq import Queue

from config.settings import settings

DEFAULT = 'default'
DOWNLOAD = 'download'
EXTRACT = 'extract'
TRANSCRIBE = 'transcribe'
SUMMARISE = 'summarise'
MONITORING = 'monitoring'


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
