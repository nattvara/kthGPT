from unittest.mock import call
from io import BytesIO
from PIL import Image
import datetime
import filecmp

from config.settings import settings
from db.crud import (
    get_image_upload_by_public_id,
)


def test_assignment_can_be_created_from_image_upload(mocker, api_client, img_file):
    mocker.patch('jobs.schedule_parse_image_upload')

    response = api_client.post(
        '/assignments/image',
        files={
            'file': ('a_file_name.png', open(img_file, 'rb'), 'image/png')
        }
    )

    image_id = response.json()['id']

    upload = get_image_upload_by_public_id(image_id)

    assert upload is not None


def test_assignments_will_not_save_the_same_image_twice(mocker, api_client, img_file):
    mocker.patch('jobs.schedule_parse_image_upload')

    def func():
        response = api_client.post(
            '/assignments/image',
            files={
                'file': ('a_file_name.png', open(img_file, 'rb'), 'image/png')
            }
        )
        return response

    response = func()
    image_id_1 = response.json()['id']

    response = func()
    image_id_2 = response.json()['id']

    assert image_id_1 == image_id_2


def test_assignments_saves_png_file_upload(mocker, api_client, img_file):
    mocker.patch('jobs.schedule_parse_image_upload')

    response = api_client.post(
        '/assignments/image',
        files={
            'file': ('a_file_name.png', open(img_file, 'rb'), 'image/png')
        }
    )

    image_id = response.json()['id']

    upload = get_image_upload_by_public_id(image_id)
    assert filecmp.cmp(img_file, upload.get_filename())


def test_assignments_can_retrieve_image(api_client, image_upload):
    response = api_client.get(f'/assignments/image/{image_upload.public_id}/img')

    image = Image.open(BytesIO(response.content))
    assert image.format == 'PNG'


def test_can_retrieve_info_from_assignments_api(api_client, image_upload):
    image_upload.text_content = 'foo'
    image_upload.description_en = 'bar'
    image_upload.description_sv = 'baz'
    image_upload.save()

    response = api_client.get(f'/assignments/image/{image_upload.public_id}')

    assert response.json()['text_content'] == 'foo'
    assert response.json()['description_en'] == 'bar'
    assert response.json()['description_sv'] == 'baz'


def test_image_upload_schedules_parse_image_upload_pipeline(mocker, api_client, img_file):
    schedule_parse_image_upload_mock = mocker.patch('jobs.schedule_parse_image_upload')

    response = api_client.post(
        '/assignments/image',
        files={
            'file': ('a_file_name.png', open(img_file, 'rb'), 'image/png')
        }
    )

    image_id = response.json()['id']
    image = get_image_upload_by_public_id(image_id)

    assert schedule_parse_image_upload_mock.call_count == 1
    assert schedule_parse_image_upload_mock.mock_calls[0] == call(image)


def test_image_upload_can_be_restarted(mocker, api_client, image_upload):
    schedule_parse_image_upload_mock = mocker.patch('jobs.schedule_parse_image_upload')

    response = api_client.post(
        f'/assignments/image/{image_upload.public_id}?restart=true',
    )

    # only schedules pipeline if not successful
    assert schedule_parse_image_upload_mock.call_count == 0
    image_upload.create_description_sv_ok = False
    image_upload.save()

    response = api_client.post(
        f'/assignments/image/{image_upload.public_id}?restart=true',
    )

    image_id = response.json()['id']
    image = get_image_upload_by_public_id(image_id)

    assert schedule_parse_image_upload_mock.call_count == 1
    assert schedule_parse_image_upload_mock.mock_calls[0] == call(image)


def test_random_upload_of_subject_can_be_retrieved(mocker, api_client, image_upload):
    image_upload.add_subject('Analysis and Calculus')

    response = api_client.get('/assignments/image/random/Analysis and Calculus')

    image_id = response.json()['id']
    image = get_image_upload_by_public_id(image_id)

    assert 'Analysis and Calculus' in image.subjects_list()


def test_assignments_respects_daily_rate_limit(mocker, api_client, random_image_generator):
    mocker.patch('jobs.start_parse_image_upload_pipeline')

    # Limit for this testcase should be 42
    assert settings.MATHPIX_DAILY_OCR_REQUESTS_LIMIT == 42

    def do_upload():
        filename = next(random_image_generator())
        response = api_client.post(
            '/assignments/image',
            files={
                'file': ('a_file_name.png', open(filename, 'rb'), 'image/png')
            }
        )
        return response

    for _ in range(settings.MATHPIX_DAILY_OCR_REQUESTS_LIMIT):
        response = do_upload()
        assert response.status_code == 200

    # Rate limit should now be exceeded
    response = do_upload()
    assert response.status_code == 500
