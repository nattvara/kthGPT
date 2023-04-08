import peewee
import uuid

from .image_upload import ImageUpload
from .lecture import Lecture
from .base import Base
from db.crud import (
    get_image_question_hits_by_image_question_id,
)


class ImageQuestion(Base):
    public_id = peewee.CharField(null=False, unique=True)
    image_upload_id = peewee.ForeignKeyField(ImageUpload, null=False, backref='imageupload', on_delete='cascade')
    query_string = peewee.TextField(null=False)

    @staticmethod
    def make_public_id() -> str:
        return str(uuid.uuid4())

    def hits(self) -> list:
        return list(get_image_question_hits_by_image_question_id(self.id))


class ImageQuestionHit(Base):
    public_id = peewee.CharField(null=False, unique=True)
    image_question_id = peewee.ForeignKeyField(ImageQuestion, null=False, backref='imagequestion', on_delete='cascade')
    lecture_id = peewee.ForeignKeyField(Lecture, null=True, backref='lecture', on_delete='set null')
    response = peewee.TextField(null=True)
    cache_is_valid = peewee.BooleanField(null=False, default=True)
    count = peewee.IntegerField(null=False, default=0)

    @staticmethod
    def make_public_id() -> str:
        return str(uuid.uuid4())
