from threading import Thread, Event
from db.models import Lecture
import tempfile
import logging
import ffmpeg
import time
import os


class ProgressFfmpeg(Thread):
    def __init__(self, vid_duration_seconds, progress_update_callback):
        Thread.__init__(self, name='ProgressFfmpeg')
        self.stop_event = Event()
        self.output_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.vid_duration_seconds = vid_duration_seconds
        self.progress_update_callback = progress_update_callback

    def run(self):
        while not self.stop_event.is_set():
            latest_progress = self.get_latest_ms_progress()
            if latest_progress is not None:
                completed_percent = latest_progress / self.vid_duration_seconds
                self.progress_update_callback(completed_percent)
            time.sleep(.01)

    def get_latest_ms_progress(self):
        lines = self.output_file.readlines()
        if lines:
            for line in lines:
                if 'out_time_ms' in line:
                    out_time_ms = line.split('=')[1]
                    return int(out_time_ms) / 1000000
        return None

    def stop(self):
        self.stop_event.set()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args, **kwargs):
        self.stop()


def download_mp4_from_m3u8(download_url: str, lecture: Lecture) -> str:
    logger = logging.getLogger('rq.worker')

    output_filename = lecture.mp4_filename()

    if os.path.isfile(output_filename):
        os.unlink(output_filename)

    lecture.mp4_progress = 0
    lecture.save()

    def on_update(progress: float):
        progress = int(progress * 100)
        logger.info(f'current progress {progress}%')
        lecture.mp4_progress = progress
        lecture.save()

    total_duration = int(float(ffmpeg.probe(download_url)['format']['duration']))
    logger.info(f'total duration {total_duration}s')

    with ProgressFfmpeg(total_duration, on_update) as progress:
        (ffmpeg
            .input(download_url)
            .output(output_filename, vcodec='copy', acodec='copy')
            .global_args('-progress', progress.output_file.name)
            .run(quiet=True))

    lecture.mp4_progress = 100
    lecture.save()
