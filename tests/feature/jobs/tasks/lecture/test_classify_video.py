from typing import Optional
import tempfile
import shutil
import os

from jobs.tasks.lecture import classify_video
from db.models import Lecture, Analysis


def test_classification_can_approve_video(mocker, mp4_file, mp3_file):
    tf = tempfile.NamedTemporaryFile(mode='w+', delete=False)
    shutil.copy(mp3_file, tf.name)

    def save_text(mp3_file: str, lecture: Lecture, output_dir: Optional[str] = None, save_progress: bool = True):
        os.mkdir(output_dir)
        filename = os.path.basename(mp3_file)
        with open(f'{output_dir}/{filename}.txt', 'w+') as file:
            file.write('One small step for man, one giant leap for mankind.')

    classification = 'Recorded lecture'

    mocker.patch('tools.youtube.download.download_mp3', return_value=tf.name)
    mocker.patch('tools.audio.transcription.save_text', side_effect=save_text)
    mocker.patch('tools.text.ai.gpt3', return_value=classification)
    schedule_analysis_of_lecture_mock = mocker.patch('jobs.schedule_analysis_of_lecture')

    lecture = Lecture(
        public_id='some_id',
        language=Lecture.Language.SWEDISH,
        mp4_filepath=mp4_file,
        source=Lecture.Source.YOUTUBE,
    )
    lecture.save()
    analysis = Analysis(lecture_id=lecture.id)
    analysis.save()

    # Classify the video
    classify_video.job(lecture.public_id, lecture.language)
    lecture.refresh()

    assert lecture.approved is True
    assert schedule_analysis_of_lecture_mock.call_count == 1

    os.unlink(tf.name)


def test_classification_can_deny_video(mocker, mp4_file, mp3_file):
    tf = tempfile.NamedTemporaryFile(mode='w+', delete=False)
    shutil.copy(mp3_file, tf.name)

    def save_text(mp3_file: str, lecture: Lecture, output_dir: Optional[str] = None, save_progress: bool = True):
        os.mkdir(output_dir)
        filename = os.path.basename(mp3_file)
        with open(f'{output_dir}/{filename}.txt', 'w+') as file:
            file.write('One small step for man, one giant leap for mankind.')

    classification = 'Some other category'

    mocker.patch('tools.youtube.download.download_mp3', return_value=tf.name)
    mocker.patch('tools.audio.transcription.save_text', side_effect=save_text)
    mocker.patch('tools.text.ai.gpt3', return_value=classification)
    schedule_analysis_of_lecture_mock = mocker.patch('jobs.schedule_analysis_of_lecture')
    schedule_fetch_of_lecture_metadata_mock = mocker.patch('jobs.schedule_fetch_of_lecture_metadata')

    lecture = Lecture(
        public_id='some_id',
        language=Lecture.Language.SWEDISH,
        mp4_filepath=mp4_file,
        source=Lecture.Source.YOUTUBE,
    )
    lecture.save()
    analysis = Analysis(lecture_id=lecture.id)
    analysis.save()

    # Classify the video
    classify_video.job(lecture.public_id, lecture.language)
    lecture.refresh()

    assert lecture.approved is False
    assert schedule_analysis_of_lecture_mock.call_count == 0

    # Even though the video got denied, we want to make sure it's easy to see
    # which video that was
    assert schedule_fetch_of_lecture_metadata_mock.call_count == 1

    os.unlink(tf.name)
