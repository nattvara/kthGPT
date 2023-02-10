import ffmpeg
import os


def extract_mp3(mp4: str, filename: str) -> str:
    if os.path.isfile(filename):
        return filename

    stream = ffmpeg.input(mp4)
    stream = ffmpeg.output(stream, filename)
    ffmpeg.run(stream)

    return filename
