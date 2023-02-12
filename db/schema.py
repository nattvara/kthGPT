from .database import db
from .models import URL, Lecture, Query


def create():
    db.connect()
    db.drop_tables([URL, Lecture, Query])
    db.create_tables([URL, Lecture, Query])
    db.close()
