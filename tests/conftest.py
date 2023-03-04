from fastapi.testclient import TestClient
import subprocess
import tempfile
import peewee
import pytest
import os

from db.schema import all_models
import api


TEST_DB_FILEPATH = '/tmp/kthgpt.test.db'


def pytest_configure(config):
    if os.path.exists(TEST_DB_FILEPATH):
        os.unlink(TEST_DB_FILEPATH)

    db = peewee.SqliteDatabase(TEST_DB_FILEPATH)
    db.create_tables(all_models)


def pytest_unconfigure(config):
    if os.path.exists(TEST_DB_FILEPATH):
        os.unlink(TEST_DB_FILEPATH)


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
