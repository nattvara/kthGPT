import peewee
import pytz
import json


from .analysis import Analysis
from tools.files.paths import (
    writable_transcript_filepath,
    writable_summary_filepath,
    writable_image_filepath,
    writable_mp4_filepath,
    writable_mp3_filepath,
)
from db.models.url import URL
from .base import Base


class Lecture(Base):
    public_id = peewee.CharField(null=False, index=True)
    language = peewee.CharField(null=False)
    approved = peewee.BooleanField(null=True)
    source = peewee.CharField(null=False, default='kth')
    length = peewee.IntegerField(null=False, default=0)
    words = peewee.IntegerField(null=False, default=0)
    title = peewee.CharField(null=True)
    date = peewee.TimestampField(null=True)
    img_preview = peewee.CharField(null=True)
    mp4_filepath = peewee.CharField(null=True)
    mp3_filepath = peewee.CharField(null=True)
    transcript_filepath = peewee.CharField(null=True)
    summary_filepath = peewee.CharField(null=True)

    class Source:
        KTH = 'kth'
        YOUTUBE = 'youtube'

    class Language:
        ENGLISH = 'en'
        SWEDISH = 'sv'

    def content_link(self):
        if self.source == self.Source.KTH:
            return f'https://play.kth.se/media/{self.public_id}'
        elif self.source == self.Source.YOUTUBE:
            return f'https://www.youtube.com/watch?v={self.public_id}'
        raise ValueError(f'unknown source {self.source}')

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

    def get_last_analysis(self):
        return (Analysis
                .filter(Analysis.lecture_id == self.id)
                .order_by(Analysis.modified_at.desc())
                .first())

    def refresh(self):
        update = Lecture.get(self.id)
        self.public_id = update.public_id
        self.language = update.language
        self.length = update.length
        self.words = update.words
        self.title = update.title
        self.date = update.date
        self.img_preview = update.img_preview
        self.mp4_filepath = update.mp4_filepath
        self.mp3_filepath = update.mp3_filepath
        self.transcript_filepath = update.transcript_filepath
        self.summary_filepath = update.summary_filepath

    def to_summary_dict(self):
        a = self.get_last_analysis()
        if a is not None:
            state = a.state
            overall_progress = a.overall_progress()
        else:
            state = None
            overall_progress = 0

        date = self.date
        if date is not None:
            tz = pytz.timezone('UTC')
            date = tz.localize(self.date, is_dst=None)
            date = date.isoformat()

        return {
            'public_id': self.public_id,
            'language': self.language,
            'title': self.title,
            'date': date,
            'state': state,
            'content_link': self.content_link(),
            'overall_progress': overall_progress,
        }

    def to_dict(self):
        a = self.get_last_analysis()
        if a is not None:
            analysis = a.to_dict()
        else:
            analysis = None

        date = self.date
        if date is not None:
            tz = pytz.timezone('UTC')
            date = tz.localize(self.date, is_dst=None)
            date = date.isoformat()

        return {
            'public_id': self.public_id,
            'language': self.language,
            'approved': self.approved,
            'source': self.source,
            'words': self.words,
            'length': self.length,
            'title': self.title,
            'date': date,
            'preview_uri': self.preview_uri(),
            'transcript_uri': self.transcript_uri(),
            'summary_uri': self.summary_uri(),
            'content_link': self.content_link(),
            'analysis': analysis,
        }
