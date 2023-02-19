import yt_dlp

from config.logger import log


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
