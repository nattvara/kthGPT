import ffmpeg
import uuid
import os

def extract_mp3(mp4: str) -> str:
    mp3 = os.path.join('tmp',f'{uuid.uuid4()}.mp3')

    stream = ffmpeg.input(mp4)
    stream = ffmpeg.output(stream, mp3)
    ffmpeg.run(stream)

    return mp3
