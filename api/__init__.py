from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from logging.config import dictConfig
from fastapi import FastAPI

from config.logger import LogConfig, log
from jobs import get_monitoring_queue
from config.settings import settings
import jobs.tasks.save_queue_info
from api.routers import (
    index,
    urls,
    lectures,
    courses,
    query,
    search,
    stats,
)


def get_app():
    app = FastAPI(title=settings.NAME, openapi_url=None)
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
    app.include_router(courses.router)
    app.include_router(query.router)
    app.include_router(search.router)
    app.include_router(stats.router)

    return app


def main():
    dictConfig(LogConfig().dict())
    log().info('starting api')

    app = get_app()

    # Reset the monitoring queue and restart the workers
    queue = next(get_monitoring_queue())
    future = datetime.utcnow() + timedelta(days=1)
    queue.scheduled_job_registry.remove_jobs(timestamp=future.timestamp())
    jobs.tasks.save_queue_info.job()

    return app
