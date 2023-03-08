import hashlib
import peewee

from .base import Base
from .lecture import Lecture


class Query(Base):
    lecture_id = peewee.ForeignKeyField(Lecture, backref='lecture')
    query_hash = peewee.CharField(index=True, null=False)
    query_string = peewee.TextField(null=False)
    count = peewee.IntegerField(null=False, default=0)
    cache_is_valid = peewee.BooleanField(null=False, default=True)
    response = peewee.TextField(null=True)

    @staticmethod
    def make_sha(string: str) -> str:
        return hashlib.sha256(string.encode()).hexdigest()

    def save(self, *args, **kwargs):
        self.query_hash = self.make_sha(self.query_string)
        return super(Query, self).save(*args, **kwargs)
