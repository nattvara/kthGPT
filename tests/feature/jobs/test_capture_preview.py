import shutil

from jobs import capture_preview
from db.models import Lecture


def test_download_of_kth_play_lecture_saves_mp4_file(mocker, mp4_file, img_file):
    def save_photo_from_video(mp4_filepath: str, output_file: str, small=False):
        shutil.copy(img_file, output_file)

    func = mocker.patch('tools.video.img.save_photo_from_video', side_effect=save_photo_from_video)

    lecture = Lecture(
        public_id='some_id',
        language=Lecture.Language.SWEDISH,
        mp4_filepath=mp4_file,
        approved=True,
        source=Lecture.Source.KTH,
    )
    lecture.save()

    capture_preview.job(lecture.public_id, lecture.language)
    lecture.refresh()

    assert lecture.img_preview == lecture.preview_filename()
    assert lecture.img_preview_small == lecture.preview_small_filename()
    assert func.call_count == 2
