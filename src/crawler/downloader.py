import youtube_dl
import uuid


def download_mp4_from_m3u8(url: str) -> str:
    filename = f'/tmp/{uuid.uuid4()}.mp4'

    ydl_opts = {
        'outtmpl': filename
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return filename
