from typing import List, Optional
from fastapi import UploadFile
import peewee
import pytz
import uuid
import json

from tools.files.paths import (
    writable_image_upload_filepath,
    get_sha_of_binary_file,
)
from .base import Base
from db.crud import (
    get_mathpix_requests_by_image_upload_id,
    get_image_questions_by_image_upload_id,
)


class ImageUpload(Base):
    public_id = peewee.CharField(null=False, unique=True)
    image_sha = peewee.CharField(null=True, unique=True)
    file_format = peewee.CharField(null=False)
    text_content = peewee.TextField(null=True)
    description_en = peewee.TextField(null=True)
    description_sv = peewee.TextField(null=True)
    search_queries_en = peewee.BlobField(null=True)
    search_queries_sv = peewee.BlobField(null=True)

    # image_search steps
    parse_image_content_ok = peewee.BooleanField(null=True)
    parse_image_content_failure_reason = peewee.TextField(null=True)
    create_description_en_ok = peewee.BooleanField(null=True)
    create_description_en_failure_reason = peewee.TextField(null=True)
    create_description_sv_ok = peewee.BooleanField(null=True)
    create_description_sv_failure_reason = peewee.TextField(null=True)
    create_search_queries_en_ok = peewee.BooleanField(null=True)
    create_search_queries_en_failure_reason = peewee.TextField(null=True)
    create_search_queries_sv_ok = peewee.BooleanField(null=True)
    create_search_queries_sv_failure_reason = peewee.TextField(null=True)

    class Language:
        ENGLISH = 'en'
        SWEDISH = 'sv'

    @staticmethod
    def make_public_id() -> str:
        return str(uuid.uuid4())

    def get_search_queries_en(self) -> Optional[List[str]]:
        val = self.search_queries_en
        if isinstance(val, str):
            return json.loads(val)
        if not isinstance(val, bytes):
            val = val.tobytes()
        return json.loads(val)

    def get_search_queries_sv(self) -> Optional[List[str]]:
        val = self.search_queries_sv
        if isinstance(val, str):
            return json.loads(val)
        if not isinstance(val, bytes):
            val = val.tobytes()
        return json.loads(val)

    def refresh(self):
        update = ImageUpload.get(self.id)
        self.file_format = update.file_format
        self.text_content = update.text_content
        self.description_en = update.description_en
        self.description_sv = update.description_sv
        self.search_queries_en = update.search_queries_en
        self.search_queries_sv = update.search_queries_sv
        self.parse_image_content_ok = update.parse_image_content_ok
        self.parse_image_content_failure_reason = update.parse_image_content_failure_reason
        self.create_description_en_ok = update.create_description_en_ok
        self.create_description_en_failure_reason = update.create_description_en_failure_reason
        self.create_description_sv_ok = update.create_description_sv_ok
        self.create_description_sv_failure_reason = update.create_description_sv_failure_reason
        self.create_search_queries_en_ok = update.create_search_queries_en_ok
        self.create_search_queries_en_failure_reason = update.create_search_queries_en_failure_reason
        self.create_search_queries_sv_ok = update.create_search_queries_sv_ok
        self.create_search_queries_sv_failure_reason = update.create_search_queries_sv_failure_reason

    def mathpix_requests(self) -> list:
        return list(get_mathpix_requests_by_image_upload_id(self.id))

    def questions(self) -> list:
        return list(get_image_questions_by_image_upload_id(self.id))

    def get_filename(self) -> str:
        return writable_image_upload_filepath(self.public_id, self.file_format)

    def save_image_data(self, upload: UploadFile):
        with open(self.get_filename(), 'wb+') as img:
            img.write(upload.file.read())

        self.image_sha = get_sha_of_binary_file(self.get_filename())
        self.save()

    def to_dict(self):
        tz = pytz.timezone('UTC')
        created_at = tz.localize(self.created_at, is_dst=None)
        modified_at = tz.localize(self.modified_at, is_dst=None)

        return {
            'id': self.public_id,
            'created_at': created_at.isoformat(),
            'modified_at': modified_at.isoformat(),
            'text_content': self.text_content,
            'description_en': self.description_en,
            'description_sv': self.description_sv,
            'parse_image_content_ok': self.parse_image_content_ok,
            'create_description_en_ok': self.create_description_en_ok,
            'create_description_sv_ok': self.create_description_sv_ok,
            'create_search_queries_en_ok': self.create_search_queries_en_ok,
            'create_search_queries_sv_ok': self.create_search_queries_sv_ok,
        }
