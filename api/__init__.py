from fastapi.middleware.cors import CORSMiddleware
from logging.config import dictConfig
from fastapi import FastAPI
import logging

from api.routers import index, urls, lectures, query
from config.logger import LogConfig, log
from config.settings import settings


def main():
    app = FastAPI(title=settings.NAME, openapi_url=None)

    dictConfig(LogConfig().dict())
    log().info('starting api')

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(index.router)
    app.include_router(urls.router)
    app.include_router(lectures.router)
    app.include_router(query.router)

    return app
