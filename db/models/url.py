import hashlib
import peewee

from .base import Base


class URL(Base):
    url = peewee.CharField(null=False, unique=True)
    url_hash = peewee.CharField(index=True, unique=True, null=False)
    lecture_id = peewee.CharField(null=True)

    @staticmethod
    def make_sha(url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()

    def lecture_uri(self, language: str):
        return f'/lectures/{self.lecture_id}/{language}'
