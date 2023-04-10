from datetime import datetime, timedelta
import peewee
import pytz
import json
import os

from .analysis import Analysis
from tools.files.paths import (
    writable_transcript_filepath,
    writable_summary_filepath,
    writable_image_filepath,
    writable_mp4_filepath,
    writable_mp3_filepath,
)
from .base import Base
from db.crud import (
    find_all_courses_relations_for_lecture_id,
    find_all_courses_for_lecture_id,
    find_all_queries_for_lecture,
)


class Lecture(Base):
    public_id = peewee.CharField(null=False, index=True)
    language = peewee.CharField(null=False)
    approved = peewee.BooleanField(null=True)
    source = peewee.CharField(null=False, default='kth')
    length = peewee.IntegerField(null=False, default=0)
    words = peewee.IntegerField(null=False, default=0)
    title = peewee.CharField(null=True)
    group = peewee.CharField(null=True)  # like a channel name on youtube
    date = peewee.TimestampField(null=True)
    description = peewee.TextField(null=True)
    raw_content_link = peewee.CharField(null=True)
    img_preview = peewee.CharField(null=True)
    img_preview_small = peewee.CharField(null=True)
    mp4_filepath = peewee.CharField(null=True)
    mp3_filepath = peewee.CharField(null=True)
    transcript_filepath = peewee.CharField(null=True)
    summary_filepath = peewee.CharField(null=True)

    class Source:
        KTH = 'kth'
        KTH_RAW = 'kth_raw'
        YOUTUBE = 'youtube'

    class Language:
        ENGLISH = 'en'
        SWEDISH = 'sv'

    def save(self, *args, **kwargs):
        self.reindex()
        return super(Lecture, self).save(*args, **kwargs)

    def reindex(self):
        # Doing import here to avoid circular import
        from jobs.tasks.lecture import index_lecture

        if self.id is not None:
            a = self.get_last_analysis()
            if a is not None:
                if a.state == Analysis.State.DENIED:
                    return
                if a.state == Analysis.State.WAITING:
                    return
                if a.state == Analysis.State.CLASSIFYING:
                    return
                if a.state == Analysis.State.FAILURE:
                    return

                from jobs import get_metadata_queue
                q = next(get_metadata_queue())
                q.enqueue(index_lecture.job, self.public_id, self.language)

    def content_link(self):
        if self.source == self.Source.KTH:
            return f'https://play.kth.se/media/{self.public_id}'
        elif self.source == self.Source.YOUTUBE:
            return f'https://www.youtube.com/watch?v={self.public_id}'
        elif self.source == self.Source.KTH_RAW:
            return f'https://play.kth.se/media/{self.public_id}'
        raise ValueError(f'unknown source {self.source}')

    def preview_filename(self):
        return writable_image_filepath(self.public_id, 'png')

    def preview_small_filename(self):
        return writable_image_filepath(self.public_id + '-small', 'png')

    def preview_uri(self):
        if self.img_preview is None:
            return None

        return f'/lectures/{self.public_id}/{self.language}/preview'

    def preview_small_uri(self):
        if self.img_preview_small is None:
            return None

        return f'/lectures/{self.public_id}/{self.language}/preview-small'

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
        filename = f'{self.transcript_filepath}/{self.public_id}.mp3.pretty.txt'
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                return file.read()

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

    def queries(self):
        queries = find_all_queries_for_lecture(self)
        return queries

    def courses(self):
        out = []

        courses = find_all_courses_for_lecture_id(self.id)
        for course in courses:
            out.append(course.to_small_dict())

        return out

    def has_course(self, course_code: str):
        for course in self.courses():
            if course['course_code'] == course_code:
                return True
        return False

    def courses_can_be_changed(self) -> bool:
        # If a lecture hasn't got any courses, they can always be added
        if len(self.courses()) == 0:
            return True

        relations = find_all_courses_relations_for_lecture_id(self.id)
        oldest_relation = None
        for relation in relations:
            if oldest_relation is None:
                oldest_relation = relation.created_at
                continue

            if relation.created_at < oldest_relation:
                oldest_relation = relation.created_at

        now = datetime.utcnow()

        # If a lecture has courses, and they where added 10 minutes ago
        # they can be changed. So an old lecture can have courses added
        relation_expires_at = oldest_relation + timedelta(minutes=10)
        if now < relation_expires_at:
            return True

        # otherwise a lectures courses cannot be changed after 1 day
        expires_at = self.created_at + timedelta(days=1)
        return now < expires_at

    def refresh(self):
        update = Lecture.get(self.id)
        self.public_id = update.public_id
        self.language = update.language
        self.length = update.length
        self.approved = update.approved
        self.words = update.words
        self.title = update.title
        self.group = update.group
        self.date = update.date
        self.description = update.description
        self.img_preview = update.img_preview
        self.img_preview_small = update.img_preview_small
        self.mp4_filepath = update.mp4_filepath
        self.mp3_filepath = update.mp3_filepath
        self.transcript_filepath = update.transcript_filepath
        self.summary_filepath = update.summary_filepath
        self.raw_content_link = update.raw_content_link

    def to_doc(self):
        course_codes = []
        for course in self.courses():
            course_codes.append(course['course_code'])

        return {
            'public_id': self.public_id,
            'language': self.language,
            'approved': self.approved,
            'source': self.source,
            'words': self.words,
            'date': self.date,
            'length': self.length,
            'title': self.title,
            'group': self.group,
            'preview_uri': self.preview_uri(),
            'preview_small_uri': self.preview_small_uri(),
            'content_link': self.content_link(),
            'courses': course_codes,
            'no_course': len(course_codes) == 0,
            'transcript': self.transcript_text(),
        }

    def to_summary_dict(self):
        a = self.get_last_analysis()
        if a is not None:
            state = a.state
            frozen = a.seems_to_have_crashed()
            overall_progress = a.overall_progress()
        else:
            state = None
            frozen = False
            overall_progress = 0

        date = self.date
        if date is not None:
            tz = pytz.timezone('UTC')
            date = tz.localize(self.date, is_dst=None)
            date = date.isoformat()

        tz = pytz.timezone('UTC')
        created_at = tz.localize(self.created_at, is_dst=None)

        return {
            'public_id': self.public_id,
            'language': self.language,
            'source': self.source,
            'created_at': created_at.isoformat(),
            'title': self.title,
            'group': self.group,
            'date': date,
            'state': state,
            'frozen': frozen,
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

        tz = pytz.timezone('UTC')
        created_at = tz.localize(self.created_at, is_dst=None)

        return {
            'public_id': self.public_id,
            'language': self.language,
            'created_at': created_at.isoformat(),
            'approved': self.approved,
            'source': self.source,
            'words': self.words,
            'length': self.length,
            'title': self.title,
            'group': self.group,
            'date': date,
            'description': self.description,
            'preview_uri': self.preview_uri(),
            'preview_small_uri': self.preview_small_uri(),
            'transcript_uri': self.transcript_uri(),
            'summary_uri': self.summary_uri(),
            'content_link': self.content_link(),
            'analysis': analysis,
            'courses': self.courses(),
            'courses_can_change': self.courses_can_be_changed(),
        }
