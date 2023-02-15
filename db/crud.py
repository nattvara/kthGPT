from typing import List, Union

from . import models


def get_url_by_sha(sha: str) -> models.URL:
    return models.URL.filter(models.URL.url_hash == sha).first()


def get_lecture_by_public_id_and_language(id: str, language: str) -> models.Lecture:
    return models.Lecture.filter(models.Lecture.public_id == id).filter(models.Lecture.language == language).first()


def get_all_lectures() -> List[models.Lecture]:
    query = models.Lecture.select().order_by(models.Lecture.created_at.asc())

    lectures = []
    for lecture in query:
        lectures.append(lecture)

    return lectures


def get_query_by_sha(lecture: models.Lecture, sha: str) -> models.Query:
    return models.Query.filter(models.Query.lecture_id == lecture.id).filter(models.Query.query_hash == sha).first()


def create_query(lecture: models.Lecture, query_string: str) -> models.Query:
    query = models.Query(lecture_id=lecture.id, query_string=query_string)
    query.save()
    return query


def save_message_for_analysis(analysis: models.Analysis, title: str, body: Union[str, None] = None):
    msg = models.Message(analysis_id=analysis.id, title=title, body=body)
    msg.save()
