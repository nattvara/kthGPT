import hashlib
import peewee
import uuid

from .image_upload import ImageUpload
from .lecture import Lecture
from .base import Base
from db.crud import (
    get_image_question_hits_by_image_question_id,
    get_image_question_by_id,
    get_image_upload_by_id,
    get_lecture_by_id,
)


class ImageQuestionHitException(Exception):
    pass


class ImageQuestion(Base):
    public_id = peewee.CharField(null=False, unique=True)
    image_upload_id = peewee.ForeignKeyField(ImageUpload, null=False, backref='imageupload', on_delete='cascade')
    query_string = peewee.TextField(null=False)
    query_hash = peewee.CharField(index=True, null=True)

    @staticmethod
    def make_public_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def make_sha(string: str) -> str:
        return hashlib.sha256(string.encode()).hexdigest()

    def hits(self) -> list:
        return list(get_image_question_hits_by_image_question_id(self.id))


class ImageQuestionHit(Base):
    public_id = peewee.CharField(null=False, unique=True)
    image_question_id = peewee.ForeignKeyField(ImageQuestion, null=False, backref='imagequestion', on_delete='cascade')
    lecture_id = peewee.ForeignKeyField(Lecture, null=True, backref='lecture', on_delete='set null')
    answer = peewee.TextField(null=True)
    relevance = peewee.TextField(null=True)
    cache_is_valid = peewee.BooleanField(null=False, default=True)
    count = peewee.IntegerField(null=False, default=0)

    @staticmethod
    def make_public_id() -> str:
        return str(uuid.uuid4())

    def refresh(self):
        update = ImageQuestionHit.get(self.id)
        self.public_id = update.public_id
        self.image_question_id = update.image_question_id
        self.lecture_id = update.lecture_id
        self.answer = update.answer
        self.relevance = update.relevance
        self.cache_is_valid = update.cache_is_valid
        self.count = update.count

    def create_answer(self, ai, prompts):
        if self.answer is not None and self.cache_is_valid:
            return

        lecture = get_lecture_by_id(self.lecture_id)
        if lecture is None:
            raise ImageQuestionHitException(f'Lecture with id {self.lecture_id} not found')

        question = get_image_question_by_id(self.image_question_id)
        if question is None:
            raise ImageQuestionHitException(f'ImageQuestion with id {self.image_question_id} not found')

        upload = get_image_upload_by_id(question.image_upload_id)
        if upload is None:
            raise ImageQuestionHitException(f'ImageUpload with id {question.image_upload_id} not found')

        prompt = prompts.create_prompt_to_answer_question_about_hit(
            lecture,
            upload,
            question,
        )

        response = ai.gpt3(
            prompt,
            time_to_live=60,
            max_retries=2,
            retry_interval=[10, 20],
            upload_id=upload.id,
        )

        self.refresh()
        self.answer = response
        self.cache_is_valid = True

    def create_relevance(self, ai, prompts):
        if self.relevance is not None and self.cache_is_valid:
            return

        lecture = get_lecture_by_id(self.lecture_id)
        if lecture is None:
            raise ImageQuestionHitException(f'Lecture with id {self.lecture_id} not found')

        question = get_image_question_by_id(self.image_question_id)
        if question is None:
            raise ImageQuestionHitException(f'ImageQuestion with id {self.image_question_id} not found')

        upload = get_image_upload_by_id(question.image_upload_id)
        if upload is None:
            raise ImageQuestionHitException(f'ImageUpload with id {question.image_upload_id} not found')

        prompt = prompts.create_prompt_to_explain_hit_relevance(
            lecture,
            upload,
            question,
        )

        response = ai.gpt3(
            prompt,
            time_to_live=60,
            max_retries=2,
            retry_interval=[10, 20],
            upload_id=upload.id,
        )

        self.refresh()
        self.relevance = response
        self.cache_is_valid = True

    def to_dict(self) -> dict:
        lecture = get_lecture_by_id(self.lecture_id)
        lecture_dict = None
        if lecture is not None:
            lecture_dict = lecture.to_dict()

        return {
            'id': self.public_id,
            'lecture': lecture_dict,
            'answer': self.answer,
            'relevance': self.relevance,
        }
