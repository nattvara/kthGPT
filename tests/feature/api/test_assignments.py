from unittest.mock import call
from io import BytesIO
from PIL import Image
import filecmp

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
