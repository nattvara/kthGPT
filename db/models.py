import datetime
import hashlib
import peewee

from tools.files.paths import (
    writable_transcript_filepath,
    writable_image_filepath,
    writable_mp4_filepath,
    writable_mp3_filepath,
)
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

    def lecture_uri(self, language: str):
        return f'/lectures/{self.lecture_id}/{language}'


class Lecture(Base):
    public_id = peewee.CharField(null=False, index=True)
    language = peewee.CharField(null=False)
    length = peewee.IntegerField(null=False, default=0)
    words = peewee.IntegerField(null=False, default=0)
    state = peewee.CharField(null=False, default='idle')
    img_preview = peewee.CharField(null=True)
    mp4_progress = peewee.IntegerField(null=False, default=0)
    mp4_filepath = peewee.CharField(null=True)
    mp3_progress = peewee.IntegerField(null=False, default=0)
    mp3_filepath = peewee.CharField(null=True)
    transcript_progress = peewee.IntegerField(null=False, default=0)
    transcript_filepath = peewee.CharField(null=True)

    class State:
        IDLE = 'idle'
        FAILURE = 'failure'
        DOWNLOADING = 'downloading'
        EXTRACTING_AUDIO = 'extracting_audio'
        TRANSCRIBING_LECTURE = 'transcribing_lecture'

    class Language:
        ENGLISH = 'en'
        SWEDISH = 'sv'

    def content_link(self):
        return f'https://play.kth.se/media/{self.public_id}'

    def preview_filename(self):
        return writable_image_filepath(self.public_id, 'png')

    def preview_uri(self):
        if self.img_preview is None:
            return None

        return f'/lectures/{self.public_id}/{self.language}/preview'

    def transcript_uri(self):
        if self.transcript_filepath is None:
            return None

        return f'/lectures/{self.public_id}/{self.language}/transcript'

    def mp4_filename(self):
        return writable_mp4_filepath(self.public_id)

    def mp3_filename(self):
        return writable_mp3_filepath(self.public_id)

    def transcript_dirname(self):
        return writable_transcript_filepath(self.public_id, self.language)

    def transcript_text(self):
        filename = f'{self.transcript_filepath}/{self.public_id}.mp3.vtt'
        with open(filename, 'r') as file:
            return file.read()

    def count_words(self):
        filename = f'{self.transcript_filepath}/{self.public_id}.mp3.txt'
        with open(filename, 'r') as file:
            return len(file.read().split(' '))

    def to_dict(self):
        return {
            'public_id': self.public_id,
            'language': self.language,
            'words': self.words,
            'length': self.length,
            'state': self.state,
            'preview_uri': self.preview_uri(),
            'transcript_uri': self.transcript_uri(),
            'content_link': self.content_link(),
            'mp4_progress': self.mp4_progress,
            'mp3_progress': self.mp3_progress,
            'transcript_progress': self.transcript_progress,
        }
