from typing import List

from . import models


def get_url_by_sha(sha: str) -> models.URL:
    return models.URL.filter(models.URL.url_hash == sha).first()


def get_lecture_by_public_id_and_language(id: str, language: str) -> models.URL:
    return models.Lecture.filter(models.Lecture.public_id == id).filter(models.Lecture.language == language).first()


def get_all_lectures() -> List[models.Lecture]:
    query = models.Lecture.select().order_by(models.Lecture.created_at.asc())

    lectures = []
    for lecture in query:
        lectures.append(lecture)

    return lectures
