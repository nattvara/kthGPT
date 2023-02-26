import ffmpeg
import os

from config.logger import log


def save_photo_from_video(mp4_filepath: str, output_file: str, small: bool = False):
    log('rq.worker').info(f'saving image from {mp4_filepath} to {output_file}')

    if os.path.isfile(output_file):
        os.unlink(output_file)

    probe = ffmpeg.probe(mp4_filepath)
    duration = float(probe['streams'][0]['duration'])
    width = probe['streams'][0]['width']

    if small:
        width = 180

    middle = int(duration / 2)
    (
        ffmpeg
        .input(mp4_filepath, ss=middle)
        .filter('scale', width, -1)
        .output(output_file, vframes=1)
        .run()
    )
