from config.settings import settings
from redis import Redis
from rq import Queue
import subprocess
import logging
import os

import jobs.save_queue_info
from config.settings import settings
from config.logger import log
from db.models import QueueInfo


def get_queues():
    cmd = [
        'rq',
        'info',
        '--url',
        f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        '--only-queues',
    ]

    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'

    log().info(f'executing command [$ {" ".join(cmd)}]')

    process = subprocess.Popen(
        cmd,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )

    return process


def get_workers():
    cmd = [
        'rq',
        'info',
        '--url',
        f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        '--only-workers',
    ]

    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'

    log().info(f'executing command [$ {" ".join(cmd)}]')

    process = subprocess.Popen(
        cmd,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )

    return process


def job():
    logger = logging.getLogger('rq.worker')

    info = QueueInfo()

    process = get_queues()
    for line in iter(process.stdout.readline, b''):
        line = line.decode()
        split = line.split(' ')
        if 'default' in line:
            info.queue_default = int(split[len(split) - 1].strip())

        if 'summarise' in line:
            info.queue_summarise = int(split[len(split) - 1].strip())

        if 'transcribe' in line:
            info.queue_transcribe = int(split[len(split) - 1].strip())

        if 'extract' in line:
            info.queue_extract = int(split[len(split) - 1].strip())

        if 'download' in line:
            info.queue_download = int(split[len(split) - 1].strip())

        if 'monitoring' in line:
            info.queue_monitoring = int(split[len(split) - 1].strip())

    worker_status = ''
    process = get_workers()
    for line in iter(process.stdout.readline, b''):
        line = line.decode()
        worker_status += line

    info.workers = worker_status

    info.save()
    log().info('done')


# Test run the job
if __name__ == '__main__':
    job()
