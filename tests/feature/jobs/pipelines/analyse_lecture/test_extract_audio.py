import shutil
import os

from jobs.pipelines.analyse_lecture import extract_audio
from db.models import Lecture, Analysis


def test_extract_audio_job_creates_mp3_from_mp4(mocker, mp4_file, mp3_file):
    def create_mp3(src_file: str, lecture: Lecture):
        shutil.copy(mp3_file, lecture.mp3_filename())
        return lecture.mp3_filename()

    mocker.patch('tools.audio.extraction.extract_mp3_from_mp4', side_effect=create_mp3)

    lecture = Lecture(
        public_id='some_id',
        language=Lecture.Language.SWEDISH,
        approved=True,
        source=Lecture.Source.KTH,
        mp4_filepath=mp4_file,
    )
    lecture.save()
    analysis = Analysis(lecture_id=lecture.id)
    analysis.save()

    extract_audio.job(lecture.public_id, lecture.language)
    lecture.refresh()

    assert lecture.get_last_analysis().mp3_progress == 100
    assert lecture.mp3_filepath == lecture.mp3_filename()
    assert os.path.exists(lecture.mp3_filename())
