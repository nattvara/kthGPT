from fastapi.testclient import TestClient
from fakeredis import FakeStrictRedis
from rq import Queue
import subprocess
import tempfile
import peewee
import pytest
import shutil
import os

from config.settings import settings
from db.schema import all_models
import api


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


def pytest_configure(config):
    settings.STORAGE_DIRECTORY = TEST_STORAGE_DIRECTORY
    settings.OPENAI_API_KEY = 'sk-xxx...'

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
