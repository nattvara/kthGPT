from PIL import Image
import tempfile
import os

from tools.video.img import save_photo_from_video


def test_photo_can_be_extracted_from_video(mp4_file):
    img_filename = tempfile.mkdtemp() + '.png'

    save_photo_from_video(mp4_file, img_filename)

    assert os.path.exists(img_filename)

    os.unlink(img_filename)


def test_low_res_photo_can_be_extracted_from_mp4(mp4_file):
    img_filename = tempfile.mkdtemp() + '.png'

    save_photo_from_video(mp4_file, img_filename, small=True)

    img = Image.open(img_filename)
    width, _ = img.size
    assert os.path.exists(img_filename)
    assert width == 180

    os.unlink(img_filename)
