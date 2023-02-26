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
)



def create():
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
    ]

    db.connect()
    db.drop_tables(all_models)
    db.create_tables(all_models)
    db.close()
