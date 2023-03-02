from yt_dlp.utils import download_range_func
import ffmpeg
import yt_dlp
import os

from config.logger import log
from db.models import Lecture


def download_mp3(url: str, output_file: str, seconds_to_download: int) -> str:
    log('rq.worker').info(f'downloading {url} to {output_file}')

    ydl_opts = {
        'format': 'best',
        'download_ranges': download_range_func(None, [(0, seconds_to_download)]),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'outtmpl': output_file + '.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return output_file + '.mp3'


def download_mp4(url: str, lecture: Lecture) -> str:
    log('rq.worker').info(f'downloading {url}')

    output_filename = lecture.mp4_filename()

    if os.path.isfile(output_filename):
        os.unlink(output_filename)

    ydl_opts = {
        'format': 'best',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'outtmpl': output_filename.replace('.mp4', '') + '.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    total_duration = int(float(ffmpeg.probe(output_filename)['format']['duration']))

    lecture.refresh()
    lecture.mp4_filepath = output_filename
    lecture.length = total_duration
    lecture.save()
