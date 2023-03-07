from typing import Optional
import os

from db.models import Lecture, Analysis
from config.settings import settings
from jobs import transcribe_audio


def test_transcription_job_runs_local_transcription_if_device_is_cuda(mocker, mp3_file):
    def create_download(
        mp3_file: str,
        lecture: Lecture,
        analysis: Analysis,
        output_dir: Optional[str] = None,
        save_progress: bool = True
    ):
        os.mkdir(output_dir)
        filename = f'{lecture.transcript_dirname()}/{lecture.public_id}.mp3.txt'
        with open(filename, 'w+') as file:
            file.write('some spoken words...')

    settings.WHISPER_TRANSCRIPTION_DEVICE = 'cuda'

    mocker.patch('db.models.lecture.Lecture.reindex')
    transcribe_locally = mocker.patch('tools.audio.transcription.transcribe_locally', side_effect=create_download)

    lecture = Lecture(
        public_id='some_id',
        language=Lecture.Language.SWEDISH,
        approved=True,
        source=Lecture.Source.KTH,
        # needs mp3_path
        mp3_filepath=mp3_file,
    )
    lecture.save()
    analysis = Analysis(lecture_id=lecture.id)
    analysis.save()

    transcribe_audio.job(lecture.public_id, lecture.language)

    lecture.refresh()

    assert lecture.get_last_analysis().transcript_progress == 100
    assert lecture.transcript_filepath == lecture.transcript_dirname()
    assert os.path.exists(lecture.transcript_dirname())
    assert transcribe_locally.call_count == 1


def test_transcription_job_runs_local_transcription_if_device_is_cpu(mocker, mp3_file):
    def create_download(
        mp3_file: str,
        lecture: Lecture,
        analysis: Analysis,
        output_dir: Optional[str] = None,
        save_progress: bool = True
    ):
        os.mkdir(output_dir)
        filename = f'{lecture.transcript_dirname()}/{lecture.public_id}.mp3.txt'
        with open(filename, 'w+') as file:
            file.write('some spoken words...')

    settings.WHISPER_TRANSCRIPTION_DEVICE = 'cpu'

    mocker.patch('db.models.lecture.Lecture.reindex')
    transcribe_locally = mocker.patch('tools.audio.transcription.transcribe_locally', side_effect=create_download)

    lecture = Lecture(
        public_id='some_id',
        language=Lecture.Language.SWEDISH,
        approved=True,
        source=Lecture.Source.KTH,
        # needs mp3_path
        mp3_filepath=mp3_file,
    )
    lecture.save()
    analysis = Analysis(lecture_id=lecture.id)
    analysis.save()

    transcribe_audio.job(lecture.public_id, lecture.language)

    lecture.refresh()

    assert lecture.get_last_analysis().transcript_progress == 100
    assert lecture.transcript_filepath == lecture.transcript_dirname()
    assert os.path.exists(lecture.transcript_dirname())
    assert transcribe_locally.call_count == 1
