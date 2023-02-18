from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from logging.config import dictConfig
from fastapi import FastAPI

from api.routers import index, urls, lectures, query
from config.logger import LogConfig, log
from jobs import get_monitoring_queue
from config.settings import settings
import jobs.save_queue_info


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

    # Reset the monitoring queue and restart the workers
    queue = next(get_monitoring_queue())
    future = datetime.utcnow() + timedelta(days=1)
    queue.scheduled_job_registry.remove_jobs(timestamp=future.timestamp())
    jobs.save_queue_info.job()

    return app
