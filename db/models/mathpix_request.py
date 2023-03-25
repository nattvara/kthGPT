import peewee

from .image_upload import ImageUpload
from .base import Base


class MathpixRequest(Base):
    image_upload_id = peewee.ForeignKeyField(ImageUpload, null=False, backref='imageupload')

    # metadata
    took_ms = peewee.IntegerField(null=False)

    # response values
    request_id = peewee.CharField(null=False)
    version = peewee.CharField(null=False)
    image_width = peewee.IntegerField(null=False)
    image_height = peewee.IntegerField(null=False)
    is_printed = peewee.BooleanField(null=False)
    is_handwritten = peewee.BooleanField(null=False)
    confidence = peewee.DecimalField(null=False)
    confidence_rate = peewee.DecimalField(null=False)
