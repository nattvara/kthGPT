import yt_dlp
import os

from config.logger import log
from db.models import Lecture


def download_mp3(url: str, output_file: str) -> str:
    log('rq.worker').info(f'downloading {url} to {output_file}')

    print(url, output_file)

    ydl_opts = {
        'format': 'bestaudio/best',
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
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'outtmpl': output_filename.replace('.mp4', '') + '.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
