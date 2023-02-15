from .database import db
from .models import URL, Lecture, Query, Analysis, Message


def create():
    db.connect()
    db.drop_tables([URL, Lecture, Query, Analysis, Message])
    db.create_tables([URL, Lecture, Query, Analysis, Message])
    db.close()
