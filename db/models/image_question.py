import peewee

from .image_upload import ImageUpload
from .base import Base


class ImageQuestion(Base):
    image_upload_id = peewee.ForeignKeyField(ImageUpload, null=False, backref='imageupload', on_delete='cascade')
    query_string = peewee.TextField(null=False)
    operationalised_query = peewee.TextField(null=True)
