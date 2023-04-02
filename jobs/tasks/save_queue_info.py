from datetime import timedelta
import subprocess
import os

from jobs import get_monitoring_queue
import jobs.tasks.save_queue_info
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

    log('rq.worker').info(f'executing command [$ {" ".join(cmd)}]')

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

    log('rq.worker').info(f'executing command [$ {" ".join(cmd)}]')

    process = subprocess.Popen(
        cmd,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )

    return process


def job():
    log('rq.worker').info('saving queue metrics')

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

        if 'approval' in line:
            info.queue_approval = int(split[len(split) - 1].strip())

        if 'metadata' in line:
            info.queue_metadata = int(split[len(split) - 1].strip())

        if 'gpt' in line:
            info.queue_gpt = int(split[len(split) - 1].strip())

    process = get_workers()
    for line in iter(process.stdout.readline, b''):
        line = line.decode()
        if 'idle' in line:
            info.workers_idle += 1

        if 'busy' in line:
            info.workers_busy += 1

    info.save()

    log('rq.worker').info('queueing next update in 30 seconds')

    queue = next(get_monitoring_queue())
    queue.enqueue_in(timedelta(seconds=30), jobs.tasks.save_queue_info.job)

    log('rq.worker').info('done.')


# Test run the job
if __name__ == '__main__':
    job()
