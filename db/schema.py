from .database import db
from .models import (
    URL,
    Lecture,
    Query,
    Analysis,
    Message,
    Course,
    CourseGroup,
    CourseLectureRelation,
    QueueInfo,
    TokenUsage,
    ImageUpload,
    ImageQuestion,
    MathpixRequest,
)


all_models = [
    URL,
    Lecture,
    Query,
    Analysis,
    Message,
    Course,
    CourseGroup,
    CourseLectureRelation,
    QueueInfo,
    TokenUsage,
    ImageUpload,
    ImageQuestion,
    MathpixRequest,
]


def create():
    db.connect()
    db.drop_tables(all_models)
    db.create_tables(all_models)
    db.close()
