import peewee
import pytz

from .base import Base


class Message(Base):
    analysis_id = peewee.IntegerField(null=False, index=True)  # not sure how to make this a foreign key field, due to circular imports
    title = peewee.CharField(null=False)
    body = peewee.TextField()

    def to_dict(self):
        tz = pytz.timezone('UTC')
        created_at = tz.localize(self.created_at, is_dst=None)
        return {
            'timestamp': created_at.isoformat(),
            'title': self.title,
            'body': self.body,
        }
