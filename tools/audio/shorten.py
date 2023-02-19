import tempfile
import logging
import ffmpeg
import os


def shorten_mp3(src_file: str, seconds: int) -> str:
    logger = logging.getLogger('rq.worker')
    logger.info(f'shortening mp3 file')

    total_duration = int(float(ffmpeg.probe(src_file)['format']['duration']))

    if total_duration < seconds:
        logger.info(f'total duration was {total_duration}s already shorter than {seconds}s')
        return

    logger.info(f'total duration was {total_duration}s shortening to {seconds}s')

    tmp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
    temp_path = f'{tmp_file.name}.mp3'

    try:
        (ffmpeg
            .input(src_file)
            .output(temp_path, acodec='copy', ss=0, t=seconds)
            .run(quiet=True))

        os.rename(temp_path, src_file)
    except ffmpeg.Error as e:
        logger.error(e.stderr)
        raise Exception('ffmpeg failed')
    finally:
        tmp_file.close()
