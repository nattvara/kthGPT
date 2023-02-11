from redis import Redis
from rq import Queue

from config.settings import settings


def get_queue() -> Queue:
    try:
        queue = Queue(connection=Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
        ))
        yield queue
    finally:
        queue.connection.close()
