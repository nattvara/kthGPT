import peewee
import uuid

from .image_upload import ImageUpload
from .base import Base


class ImageQuestion(Base):
    public_id = peewee.CharField(null=False, unique=True)
    image_upload_id = peewee.ForeignKeyField(ImageUpload, null=False, backref='imageupload', on_delete='cascade')
    query_string = peewee.TextField(null=False)

    @staticmethod
    def make_public_id() -> str:
        return str(uuid.uuid4())
