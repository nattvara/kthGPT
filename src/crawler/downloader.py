import youtube_dl
import os


def download_mp4_from_m3u8(download_url: str, filename: str) -> str:
    if os.path.isfile(filename):
        return filename

    ydl_opts = {
        'outtmpl': filename
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([download_url])

    return filename
