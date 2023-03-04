import shutil
import os

from tools.ffmpeg.progress import ProgressFFmpeg
from db.models import Lecture, Analysis
from jobs import download_lecture

def test_download_of_kth_play_lecture_saves_mp4_file(mocker, mp4_file):
    def create_download(
        download_url: str,
        output_filename: str,
        progress: ProgressFFmpeg,
    ):
        shutil.copy(mp4_file, output_filename)

    mocker.patch('tools.web.crawler.get_m3u8', return_value='https://example.com/index.m3u8')
    mocker.patch('ffmpeg.probe', return_value={'format': {'duration': 10}})
    mocker.patch('tools.web.downloader.run_ffmpeg_cmd', side_effect=create_download)

    lecture = Lecture(
        public_id='some_id',
        language=Lecture.Language.SWEDISH,
        approved=True,
        source=Lecture.Source.KTH,
    )
    lecture.save()
    analysis = Analysis(lecture_id=lecture.id)
    analysis.save()
    print(lecture.get_last_analysis())

    download_lecture.job(lecture.public_id, lecture.language)
    lecture.refresh()

    print(lecture.get_last_analysis())
    assert lecture.get_last_analysis().mp4_progress == 100
    assert lecture.mp4_filepath == lecture.mp4_filename()
    assert os.path.exists(lecture.mp4_filename())
