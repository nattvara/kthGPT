from typing import List

from . import models


def get_url_by_sha(sha: str) -> models.URL:
    return models.URL.filter(models.URL.url_hash == sha).first()


def get_lecture_by_public_id(id: str) -> models.URL:
    return models.Lecture.filter(models.Lecture.public_id == id).first()


def get_all_lectures() -> List[models.Lecture]:
    query = models.Lecture.select()

    lectures = []
    for lecture in query:
        lectures.append(lecture)

    return lectures


def get_lecture(public_id: str) -> models.Lecture:
    return models.Lecture.filter(models.Lecture.public_id == public_id).first()
