from typing import BinaryIO
import tempfile
import hashlib
import os

from config.settings import settings


def create_root_if_not_exists():
    if not os.path.isdir(settings.STORAGE_DIRECTORY):
        os.mkdir(settings.STORAGE_DIRECTORY)


def writable_image_filepath(name: str, extension: str) -> str:
    create_root_if_not_exists()

    directory = os.path.join(settings.STORAGE_DIRECTORY, 'img')
    if not os.path.isdir(directory):
        os.mkdir(directory)

    return os.path.join(directory, f'{name}.{extension}')


def writable_mp4_filepath(name: str) -> str:
    create_root_if_not_exists()

    directory = os.path.join(settings.STORAGE_DIRECTORY, 'mp4')
    if not os.path.isdir(directory):
        os.mkdir(directory)

    return os.path.join(directory, f'{name}.mp4')


def writable_mp3_filepath(name: str) -> str:
    create_root_if_not_exists()

    directory = os.path.join(settings.STORAGE_DIRECTORY, 'mp3')
    if not os.path.isdir(directory):
        os.mkdir(directory)

    return os.path.join(directory, f'{name}.mp3')


def writable_transcript_filepath(name: str, language: str) -> str:
    create_root_if_not_exists()

    directory = os.path.join(settings.STORAGE_DIRECTORY, 'transcripts')
    if not os.path.isdir(directory):
        os.mkdir(directory)

    return os.path.join(directory, f'{name}-{language}')


def writable_summary_filepath(name: str, language: str) -> str:
    create_root_if_not_exists()

    directory = os.path.join(settings.STORAGE_DIRECTORY, 'summaries')
    if not os.path.isdir(directory):
        os.mkdir(directory)

    return os.path.join(directory, f'{name}-{language}')


def writable_image_upload_filepath(name: str, extension: str) -> str:
    create_root_if_not_exists()

    directory = os.path.join(settings.STORAGE_DIRECTORY, 'img_uploads')
    if not os.path.isdir(directory):
        os.mkdir(directory)

    return os.path.join(directory, f'{name}.{extension}')


def get_sha_of_binary_file(filename: str) -> str:
    with open(filename, 'rb', buffering=0) as img:
        sha256_hash = hashlib.sha256(img.read())
        return sha256_hash.hexdigest()


def get_sha_of_binary_file_descriptor(file: BinaryIO) -> str:
    tf = tempfile.NamedTemporaryFile(mode='wb+', delete=False)
    with open(tf.name, 'wb+') as f:
        f.write(file.read())

    # reset seek so descriptor has no side effects
    file.seek(0)

    sha = get_sha_of_binary_file(tf.name)

    tf.close()
    os.unlink(tf.name)

    return sha
