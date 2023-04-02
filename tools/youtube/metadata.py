from datetime import datetime
import yt_dlp


def get_upload_date(url: str) -> datetime:
    ydl_opts = {
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        sanitized = ydl.sanitize_info(info)

        upload_date = sanitized['upload_date']
        date = datetime.strptime(upload_date, '%Y%m%d')
        return date


def get_channel_name(url: str) -> str:
    ydl_opts = {
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        sanitized = ydl.sanitize_info(info)

        return sanitized['channel']
