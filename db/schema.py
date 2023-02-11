from .database import db
from .models import URL, Lecture


def create():
    db.connect()
    db.drop_tables([URL, Lecture])
    db.create_tables([URL, Lecture])
    db.close()
