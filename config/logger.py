from pydantic import BaseModel
import logging

from config.settings import settings


class LogConfig(BaseModel):
    LOGGER_NAME: str = settings.NAME
    LOG_FORMAT: str = '%(levelprefix)s | %(asctime)s | %(message)s'
    LOG_LEVEL: str = 'DEBUG'

    version = 1
    disable_existing_loggers = False
    formatters = {
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': LOG_FORMAT,
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    }
    handlers = {
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
    }
    loggers = {
        LOGGER_NAME: {'handlers': ['default'], 'level': LOG_LEVEL},
    }


def log(logger_name=settings.NAME):
    return logging.getLogger(logger_name)
