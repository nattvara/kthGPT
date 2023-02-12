import datetime
import hashlib
import peewee
import json

from tools.files.paths import (
    writable_transcript_filepath,
    writable_summary_filepath,
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
    summary_progress = peewee.IntegerField(null=False, default=0)
    summary_filepath = peewee.CharField(null=True)

    class State:
        IDLE = 'idle'
        FAILURE = 'failure'
        DOWNLOADING = 'downloading'
        EXTRACTING_AUDIO = 'extracting_audio'
        TRANSCRIBING_LECTURE = 'transcribing_lecture'
        SUMMARISING_LECTURE = 'summarising_lecture'
        READY = 'ready'

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

    def summary_uri(self):
        if self.summary_filepath is None:
            return None

        return f'/lectures/{self.public_id}/{self.language}/summary'

    def mp4_filename(self):
        return writable_mp4_filepath(self.public_id)

    def mp3_filename(self):
        return writable_mp3_filepath(self.public_id)

    def transcript_dirname(self):
        return writable_transcript_filepath(self.public_id, self.language)

    def summary_filename(self):
        return writable_summary_filepath(self.public_id, self.language)

    def transcript_text(self):
        filename = f'{self.transcript_filepath}/{self.public_id}.mp3.vtt'
        with open(filename, 'r') as file:
            return file.read()

    def summary_text(self):
        with open(self.summary_filepath, 'r') as file:
            return file.read()

    def count_words(self):
        filename = f'{self.transcript_filepath}/{self.public_id}.mp3.txt'
        with open(filename, 'r') as file:
            return len(file.read().split(' '))

    def get_segments(self):
        if self.transcript_filepath is None:
            return None

        filename = f'{self.transcript_filepath}/{self.public_id}.mp3.json'
        with open(filename, 'r') as file:
            return json.load(file)['segments']

    def overall_progress(self):
        mp4_weight = 1
        mp3_weight = 3
        transcript_weight = 15
        summary_weight = 5

        weighted_mp4 = self.mp4_progress * mp4_weight
        weighted_mp3 = self.mp3_progress * mp3_weight
        weighted_transcript = self.transcript_progress * transcript_weight
        weighted_summary = self.summary_progress * summary_weight

        total_weight = mp4_weight + mp3_weight + transcript_weight + summary_weight
        return int((weighted_mp4 + weighted_mp3 + weighted_transcript + weighted_summary) / total_weight)

    def to_summary_dict(self):
        return {
            'public_id': self.public_id,
            'language': self.language,
            'state': self.state,
            'content_link': self.content_link(),
            'overall_progress': self.overall_progress(),
        }

    def to_dict(self):
        return {
            'public_id': self.public_id,
            'language': self.language,
            'words': self.words,
            'length': self.length,
            'state': self.state,
            'preview_uri': self.preview_uri(),
            'transcript_uri': self.transcript_uri(),
            'summary_uri': self.summary_uri(),
            'content_link': self.content_link(),
            'mp4_progress': self.mp4_progress,
            'mp3_progress': self.mp3_progress,
            'transcript_progress': self.transcript_progress,
            'summary_progress': self.summary_progress,
            'overall_progress': self.overall_progress(),
        }


class Query(Base):
    lecture_id = peewee.ForeignKeyField(Lecture, backref='lecture')
    query_hash = peewee.CharField(index=True, unique=True, null=False)
    query_string = peewee.TextField(null=False)
    response = peewee.TextField(null=True)

    @staticmethod
    def make_sha(string: str) -> str:
        return hashlib.sha256(string.encode()).hexdigest()

    def save(self, *args, **kwargs):
        self.query_hash = self.make_sha(self.query_string)
        return super(Query, self).save(*args, **kwargs)
