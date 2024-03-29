from fastapi.testclient import TestClient
from db.models import Lecture, Analysis
from fakeredis import FakeStrictRedis
from rq import Queue
from PIL import Image
import subprocess
import tempfile
import peewee
import random
import pytest
import shutil
import json
import os

from db.models import ImageUpload, ImageQuestion
from config.settings import settings
from db.schema import all_models
import api

TEST_API_ENDPOINT = 'https://example.com'
TEST_MATHPIX_APP_ID = 'some_id'
TEST_MATHPIX_APP_KEY = 'some_key'

TEST_DB_FILEPATH = '/tmp/kthgpt.test.db'
TEST_STORAGE_DIRECTORY = '/tmp/kthgpt-test-filesystem'

QUEUE_DEFAULT = 'fake_default'
QUEUE_DOWNLOAD = 'fake_download'
QUEUE_EXTRACT = 'fake_extract'
QUEUE_TRANSCRIBE = 'fake_transcribe'
QUEUE_SUMMARISE = 'fake_summarise'
QUEUE_MONITORING = 'fake_monitoring'
QUEUE_APPROVAL = 'fake_approval'
QUEUE_GPT = 'fake_gpt'
QUEUE_METADATA = 'fake_metadata'
QUEUE_IMAGE = 'fake_image'
QUEUE_IMAGE_METADATA = 'fake_image_metadata'
QUEUE_CLASSIFICATIONS = 'fake_classifications'


def pytest_configure(config):
    settings.STORAGE_DIRECTORY = TEST_STORAGE_DIRECTORY
    settings.OPENAI_API_KEY = 'sk-xxx...'
    settings.API_ENDPOINT = TEST_API_ENDPOINT

    settings.MATHPIX_APP_ID = TEST_MATHPIX_APP_ID
    settings.MATHPIX_APP_KEY = TEST_MATHPIX_APP_KEY
    settings.MATHPIX_DAILY_OCR_REQUESTS_LIMIT = 42

    if os.path.exists(TEST_DB_FILEPATH):
        os.unlink(TEST_DB_FILEPATH)

    db = peewee.SqliteDatabase(TEST_DB_FILEPATH)
    db.create_tables(all_models)


def pytest_unconfigure(config):
    if os.path.exists(TEST_DB_FILEPATH):
        os.unlink(TEST_DB_FILEPATH)

    if os.path.exists(TEST_STORAGE_DIRECTORY):
        shutil.rmtree(TEST_STORAGE_DIRECTORY)


def get_fake_queue(name):
    queue = Queue(
        name=name,
        is_async=False,
        connection=FakeStrictRedis()
    )
    yield queue


@pytest.fixture(autouse=True)
def run_around_tests(mocker):
    db = peewee.SqliteDatabase(TEST_DB_FILEPATH)
    setup(db)

    mocker.patch('jobs.get_default_queue', return_value=get_fake_queue(QUEUE_DEFAULT))
    mocker.patch('jobs.get_download_queue', return_value=get_fake_queue(QUEUE_DOWNLOAD))
    mocker.patch('jobs.get_extract_queue', return_value=get_fake_queue(QUEUE_EXTRACT))
    mocker.patch('jobs.get_transcribe_queue', return_value=get_fake_queue(QUEUE_TRANSCRIBE))
    mocker.patch('jobs.get_summarise_queue', return_value=get_fake_queue(QUEUE_SUMMARISE))
    mocker.patch('jobs.get_monitoring_queue', return_value=get_fake_queue(QUEUE_MONITORING))
    mocker.patch('jobs.get_approval_queue', return_value=get_fake_queue(QUEUE_APPROVAL))
    mocker.patch('jobs.get_metadata_queue', return_value=get_fake_queue(QUEUE_METADATA))
    mocker.patch('jobs.get_image_queue', return_value=get_fake_queue(QUEUE_IMAGE))
    mocker.patch('jobs.get_image_metadata_queue', return_value=get_fake_queue(QUEUE_IMAGE_METADATA))
    mocker.patch('jobs.get_classifications_queue', return_value=get_fake_queue(QUEUE_CLASSIFICATIONS))

    yield
    teardown(db)


def setup(db):
    db.create_tables(all_models)


def teardown(db):
    db.drop_tables(all_models)


@pytest.fixture
def api_client():
    client = TestClient(api.get_app())
    return client


@pytest.fixture
def analysed_lecture():
    id = 'some_id'

    lecture = Lecture(
        public_id=id,
        language='sv',
        approved=True,
        title='A lecture',
        description='some description',
    )
    lecture.save()

    analysis = Analysis(lecture_id=lecture.id)
    analysis.save()

    save_dummy_summary_for_lecture(lecture)
    save_dummy_transcript_for_lecture(lecture)

    return lecture


def save_dummy_summary_for_lecture(lecture: Lecture):
    summary_filename = lecture.summary_filename()
    if os.path.isfile(summary_filename):
        os.unlink(summary_filename)

    with open(summary_filename, 'w+') as file:
        file.write('some summary')

    lecture.summary_filepath = summary_filename
    lecture.save()


def save_dummy_transcript_for_lecture(lecture: Lecture):
    transcript_dirname = lecture.transcript_dirname()
    if os.path.exists(transcript_dirname):
        shutil.rmtree(transcript_dirname, ignore_errors=True)

    os.mkdir(transcript_dirname)

    transcript_filename = f'{transcript_dirname}/{lecture.public_id}.mp3.pretty.txt'
    with open(transcript_filename, 'w+') as file:
        file.write('transcript content...')

    lecture.transcript_filepath = transcript_dirname
    lecture.save()


@pytest.fixture
def image_upload(img_file):
    _, extension = os.path.splitext(img_file)

    image = ImageUpload(
        public_id=ImageUpload.make_public_id(),
        file_format=extension.replace('.', ''),
        search_queries_sv=json.dumps(['fråga 1', 'fråga 2']),
        search_queries_en=json.dumps(['query 1', 'query 2']),
        parse_image_content_ok=True,
        create_title_ok=True,
        create_description_en_ok=True,
        create_description_sv_ok=True,
        create_search_queries_en_ok=True,
        create_search_queries_sv_ok=True,
        classify_subjects_ok=True,
    )
    image.save()

    with open(image.get_filename(), 'wb+') as img:
        with open(img_file, 'rb') as src:
            img.write(src.read())

    return image


@pytest.fixture
def image_question(image_upload):
    question = ImageQuestion(
        public_id=ImageQuestion.make_public_id(),
        image_upload_id=image_upload.id,
        query_string='help me',
    )
    question.save()

    return question


@pytest.fixture
def mp4_file():
    tf = tempfile.NamedTemporaryFile(
        mode='w+',
        delete=False,
        suffix='.mp4'
    )
    length = 3  # length in seconds

    cmd = [
        'ffmpeg',
        '-y',
        '-f',
        'lavfi',
        '-i',
        'testsrc=size=1920x1080:rate=1',
        '-vf',
        'hue=s=0',
        '-vcodec',
        'libx264',
        '-preset',
        'superfast',
        '-tune',
        'zerolatency',
        '-pix_fmt',
        'yuv420p',
        '-t',
        str(length),
        '-movflags',
        '+faststart',
        tf.name,
    ]

    env = os.environ.copy()

    process = subprocess.Popen(
        cmd,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )
    process.wait()

    yield tf.name

    tf.close()
    os.unlink(tf.name)


@pytest.fixture
def mp3_file():
    return os.path.join(os.path.dirname(__file__), 'files') + '/example.mp3'


@pytest.fixture
def img_file():
    return os.path.join(os.path.dirname(__file__), 'files') + '/example.png'


@pytest.fixture
def random_image_generator():
    def create_random_image():
        tf = tempfile.NamedTemporaryFile(
            mode='w+',
            delete=False,
            suffix='.png'
        )

        width = 100
        height = 100

        img = Image.new('RGB', (width, height))

        for x in range(width):
            for y in range(height):
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                img.putpixel((x, y), (r, g, b))

        img.save(tf.name)
        yield tf.name

        tf.close()
        os.unlink(tf.name)

    return create_random_image


@pytest.fixture
def make_mocked_classifier():
    def helper_func(labels, err=None):
        class ClassifierMock:
            def __init__(self) -> None:
                pass

            def classify(self, text: str) -> list:
                if err:
                    raise err
                return labels

        return ClassifierMock()

    return helper_func
