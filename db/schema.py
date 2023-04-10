from .database import db
from .models import (
    URL,
    Lecture,
    LectureSubject,
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
    LectureSubject,
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
