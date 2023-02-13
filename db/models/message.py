import hashlib
import peewee

from .base import Base


class Message(Base):
    analysis_id = peewee.IntegerField(null=False, index=True)  # not sure how to make this a foreign key field, due to circular imports
    title = peewee.CharField(null=False)
    body = peewee.TextField()

    def to_dict(self):
        return {
            'timestamp': self.created_at,
            'title': self.title,
            'body': self.body,
        }
