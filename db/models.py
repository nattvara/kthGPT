import datetime
import hashlib
import peewee

from tools.files.paths import writable_image_filepath
from .database import db


class Base(peewee.Model):
    created_at = peewee.DateTimeField(default=datetime.datetime.now, null=False)
    modified_at = peewee.DateTimeField(default=datetime.datetime.now, null=False)

    class Meta:
        database = db

    class Config:
        orm_mode = True

    def save(self, *args, **kwargs):
        self.modified_at = datetime.datetime.now()
        return super(Base, self).save(*args, **kwargs)


class URL(Base):
    url = peewee.CharField(null=False, unique=True)
    url_hash = peewee.CharField(index=True, unique=True, null=False)
    lecture_id = peewee.CharField(null=True)

    @staticmethod
    def make_sha(url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()

    def to_dict(self):
        return {
            'lecture_id': self.lecture_id,
            'url': self.url,
            'url_hash': self.url_hash,
        }


class Lecture(Base):
    public_id = peewee.CharField(null=False, index=True, unique=True)
    img_preview = peewee.CharField(null=True)
    mp4_progress = peewee.IntegerField(null=False, default=0)
    mp4_filepath = peewee.CharField(null=True)

    def content_link(self):
        return f'https://play.kth.se/media/{self.public_id}'

    def preview_filename(self):
        return writable_image_filepath(self.public_id, 'png')

    def preview_uri(self):
        if self.img_preview is None:
            return None

        return f'/lectures/{self.public_id}/preview'

    def to_dict(self):
        return {
            'public_id': self.public_id,
            'preview_uri': self.preview_uri(),
            'content_link': self.content_link(),
        }
