from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from config.settings import settings
from api.routers import index, urls, lectures


def main():
    app = FastAPI(title=settings.NAME)

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

    return app
