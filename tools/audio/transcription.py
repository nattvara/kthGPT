from pydub import AudioSegment
from typing import Optional
import subprocess
import tempfile
import logging
import shutil
import ffmpeg
import openai
import json
import math
import re
import os


from db.crud import save_message_for_analysis
from db.models import Lecture, Analysis
from config.settings import settings


def save_text(
    mp3_file: str,
    lecture: Lecture,
    output_dir: Optional[str] = None,
    save_progress: bool = True
):
    analysis = None
    if save_progress:
        lecture.refresh()
        analysis = lecture.get_last_analysis()
        analysis.transcript_progress = 0
        analysis.save()

    if output_dir is None:
        output_dir = lecture.transcript_dirname()

    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir, ignore_errors=False)

    if settings.WHISPER_TRANSCRIPTION_DEVICE in ['cuda', 'cpu']:
        transcribe_locally(
            mp3_file,
            lecture,
            analysis,
            output_dir,
            save_progress,
        )
    elif settings.WHISPER_TRANSCRIPTION_DEVICE == 'openai':
        transcribe_openai(
            mp3_file,
            lecture,
            analysis,
            output_dir,
            save_progress,
        )
    else:
        raise ValueError(f'unknown transcription device: {settings.WHISPER_TRANSCRIPTION_DEVICE}')

    if save_progress:
        lecture.refresh()
        lecture.transcript_filepath = output_dir
        lecture.save()

        analysis = lecture.get_last_analysis()
        lecture.transcript_progress = 100
        analysis.save()


def transcribe_openai(
    mp3_file: str,
    lecture: Lecture,
    analysis: Optional[Analysis] = None,
    output_dir: Optional[str] = None,
    save_progress: bool = True
):
    logger = logging.getLogger('rq.worker')

    openai.api_key = settings.OPENAI_API_KEY

    os.mkdir(output_dir)

    audio = AudioSegment.from_mp3(mp3_file)
    length = len(audio)

    logger.info(f'total duration {length / 1000}s')

    step_size = 10  # number of minutes to do at once
    current_time = 0

    parts = math.ceil(length / 1000 / 60 / step_size)

    text = ''
    segments = []

    inc = 0
    while current_time < length:
        inc += 1

        if save_progress:
            lecture.refresh()
            analysis = lecture.get_last_analysis()
            save_message_for_analysis(analysis, 'Creating transcript...', f'Currently on part {inc}/{parts}.')  # noqa: E501

        step_start = current_time
        step_end = current_time + step_size * 1000 * 60

        sample = audio[step_start:step_end]

        temp_path = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.mp3')
        temp_path.close()
        sample.export(temp_path.name, format='mp3')

        with open(temp_path.name, 'rb') as file:
            response = openai.Audio.transcribe(
                'whisper-1',
                file,
                response_format='verbose_json',
                language=lecture.language,
            )
            text += f'{response["text"]} '
            for segment in response['segments']:
                segment['start'] = segment['start'] + step_start / 1000
                segment['end'] = segment['end'] + step_start / 1000
                segment['seek'] = segment['seek'] + step_start
                segments.append(segment)

        os.unlink(temp_path.name)
        current_time = step_end

        if not save_progress:
            continue

        progress = int((inc / parts) * 100)
        logger.info(f'current progress {progress}%')
        lecture.refresh()
        analysis = lecture.get_last_analysis()
        analysis.transcript_progress = progress
        analysis.save()

    filename = os.path.basename(mp3_file)
    with open(f'{output_dir}/{filename}.txt', 'w+') as file:
        file.write(text)

    with open(f'{output_dir}/{filename}.json', 'w+') as file:
        json.dump({'segments': segments}, file)

    with open(f'{output_dir}/{filename}.pretty.txt', 'w+') as file:
        def seconds_to_time_string(seconds):
            minutes = seconds // 60
            seconds = seconds % 60
            return f'{minutes:02d}:{seconds:02d}'

        for segment in segments:
            line = ''
            line += seconds_to_time_string(round(segment['start']))
            line += ' -> '
            line += seconds_to_time_string(round(segment['end']))
            line += ': '
            line += segment['text']
            line += '\n'
            file.write(line)


def transcribe_locally(
    mp3_file: str,
    lecture: Lecture,
    analysis: Optional[Analysis] = None,
    output_dir: Optional[str] = None,
    save_progress: bool = True
):
    logger = logging.getLogger('rq.worker')

    total_duration = int(float(ffmpeg.probe(mp3_file)['format']['duration']))
    logger.info(f'total duration {total_duration}s')

    if lecture.language == Lecture.Language.ENGLISH:
        lang = 'en'
        model = 'tiny'
        if settings.WHISPER_TRANSCRIPTION_DEVICE == 'cuda':
            model = 'small'
    elif lecture.language == Lecture.Language.SWEDISH:
        lang = 'sv'
        model = 'small'
    if lecture.source == Lecture.Source.KTH_RAW:
        model = 'medium'

    cmd = [
        'whisper',
        mp3_file,
        f'--model={model}',
        f'--language={lang}',
        f'--output_dir={output_dir}',
        f'--device={settings.WHISPER_TRANSCRIPTION_DEVICE}',
        '--verbose=True',
    ]

    whisper_env = os.environ.copy()
    whisper_env['PYTHONUNBUFFERED'] = '1'

    logger.info(f'executing command [$ {" ".join(cmd)}]')

    # Using a subprocess instead of the python api, since the python
    # api doesn't support accessing the progress
    process = subprocess.Popen(
        cmd,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=whisper_env,
    )

    regex = r'^\[(\d\d:\d\d(:\d\d)*).*$'
    for line in iter(process.stdout.readline, b''):
        line = line.decode()

        if not save_progress:
            continue

        if not re.match(regex, line):
            continue

        matches = re.finditer(regex, line, re.MULTILINE)

        match = next(matches)
        if match:
            if len(match.group(1).split(':')) == 3:
                hours, minutes, seconds = match.group(1).split(':')
                current = int(hours) * 60 * 60 + int(minutes) * 60 + int(seconds)
                timestamp = f'{hours}:{minutes}:{seconds}'
            else:
                minutes, seconds = match.group(1).split(':')
                current = int(minutes) * 60 + int(seconds)
                timestamp = f'{minutes}:{seconds}'

            save_message_for_analysis(analysis, 'Creating transcript...', f'This is usually what takes the longest time. Currently at {timestamp} in the lecture.')  # noqa: E501

            progress = int((current / total_duration) * 100)

            logger.info(f'current progress {progress}%')
            lecture.refresh()
            analysis = lecture.get_last_analysis()
            analysis.transcript_progress = progress
            analysis.save()

    process.stdout.close()
