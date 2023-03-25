from fastapi import UploadFile
import peewee
import pytz
import uuid

from tools.files.paths import writable_image_upload_filepath
from .base import Base


class ImageUpload(Base):
    public_id = peewee.CharField(null=False, unique=True)
    file_format = peewee.CharField(null=False)
    text_content = peewee.TextField(null=True)
    description = peewee.TextField(null=True)
    search_queries_en = peewee.BlobField(null=True)
    search_queries_sv = peewee.BlobField(null=True)

    @staticmethod
    def make_public_id() -> str:
        return str(uuid.uuid4())

    def refresh(self):
        update = ImageUpload.get(self.id)
        self.file_format = update.file_format
        self.text_content = update.text_content
        self.description = update.description
        self.search_queries_en = update.search_queries_en
        self.search_queries_sv = update.search_queries_sv

    def get_filename(self) -> str:
        return writable_image_upload_filepath(self.public_id, self.file_format)

    def save_image_data(self, upload: UploadFile):
        with open(self.get_filename(), 'wb+') as img:
            img.write(upload.file.read())

    def to_dict(self):
        tz = pytz.timezone('UTC')
        created_at = tz.localize(self.created_at, is_dst=None)
        modified_at = tz.localize(self.modified_at, is_dst=None)

        return {
            'id': self.public_id,
            'created_at': created_at.isoformat(),
            'modified_at': modified_at.isoformat(),
            'text_content': self.text_content,
            'description': self.description,
        }
