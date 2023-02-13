from tools.ffmpeg.progress import ProgressFFmpeg
from db.models import Lecture
import logging
import ffmpeg
import os


def extract_mp3_from_mp4(src_file: str, lecture: Lecture) -> str:
    logger = logging.getLogger('rq.worker')

    output_filename = lecture.mp3_filename()

    if os.path.isfile(output_filename):
        os.unlink(output_filename)

    lecture.refresh()
    lecture.mp3_progress = 0
    lecture.save()

    def on_update(progress: float):
        progress = int(progress * 100)
        logger.info(f'current progress {progress}%')
        lecture.refresh()
        lecture.mp3_progress = progress
        lecture.save()

    total_duration = int(float(ffmpeg.probe(src_file)['format']['duration']))
    logger.info(f'total duration {total_duration}s')

    with ProgressFFmpeg(total_duration, on_update) as progress:
        try:
            (ffmpeg
                .input(src_file)
                .output(output_filename)
                .global_args('-progress', progress.output_file.name)
                .run(quiet=True))
        except ffmpeg.Error as e:
            logger.error(e.stderr)
            lecture.refresh()
            lecture.state = Lecture.State.FAILURE
            lecture.save()
            raise Exception('ffmpeg failed')

    lecture.refresh()
    lecture.mp3_progress = 100
    lecture.mp3_filepath = output_filename
    lecture.save()
