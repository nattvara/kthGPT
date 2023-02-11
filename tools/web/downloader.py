from tools.ffmpeg.progress import ProgressFFmpeg
from db.models import Lecture
import logging
import ffmpeg
import os


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

    with ProgressFFmpeg(total_duration, on_update) as progress:
        try:
            (ffmpeg
                .input(download_url)
                .output(output_filename, vcodec='copy', acodec='copy')
                .global_args('-progress', progress.output_file.name)
                .run(quiet=True))
        except ffmpeg.Error as e:
            logger.error(e.stderr)
            lecture.state = Lecture.State.FAILURE
            lecture.save()
            raise Exception('ffmpeg failed')

    lecture.mp4_progress = 100
    lecture.mp4_filepath = output_filename
    lecture.length = total_duration
    lecture.save()
