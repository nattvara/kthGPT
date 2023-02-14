from db.crud import save_message_for_analysis
from db.models import Lecture
import subprocess
import logging
import shutil
import ffmpeg
import re
import os


MODEL = 'tiny'


def save_text(mp3_file: str, lecture: Lecture):
    logger = logging.getLogger('rq.worker')

    lecture.refresh()
    analysis = lecture.get_last_analysis()
    analysis.transcript_progress = 0
    analysis.save()

    total_duration = int(float(ffmpeg.probe(mp3_file)['format']['duration']))
    logger.info(f'total duration {total_duration}s')

    output_dir = lecture.transcript_dirname()

    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir, ignore_errors=False)

    if lecture.language == Lecture.Language.ENGLISH:
        lang = 'en'
    elif lecture.language == Lecture.Language.SWEDISH:
        lang = 'sv'

    cmd = [
        'whisper',
        mp3_file,
        f'--model={MODEL}',
        f'--language={lang}',
        f'--output_dir={output_dir}',
        '--verbose=True',
    ]

    if lang != 'en':
        cmd.append('--task translate')

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

            save_message_for_analysis(analysis, 'Creating transcript...', f'This is usually what takes the longest time. Currently at {timestamp} in the lecture.')

            progress = int((current / total_duration) * 100)

            logger.info(f'current progress {progress}%')
            lecture.refresh()
            analysis = lecture.get_last_analysis()
            analysis.transcript_progress = progress
            analysis.save()

    lecture.refresh()
    lecture.transcript_filepath = output_dir
    lecture.save()

    analysis = lecture.get_last_analysis()
    lecture.transcript_progress = 100
    analysis.save()

    process.stdout.close()
