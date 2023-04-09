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
    ImageUploadSubject,
    ImageQuestion,
    ImageQuestionHit,
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
    ImageUploadSubject,
    ImageQuestion,
    ImageQuestionHit,
    MathpixRequest,
]


def create():
    db.connect()
    db.drop_tables(all_models)
    db.create_tables(all_models)
    db.close()
