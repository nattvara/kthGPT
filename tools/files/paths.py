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
