import peewee
import pytz

from .base import Base


class Message(Base):
    analysis_id = peewee.IntegerField(null=False, index=True)  # not sure how to make this a foreign key field, due to circular imports
    title = peewee.CharField(null=False)
    body = peewee.TextField()

    def to_dict(self):
        tz = pytz.timezone('UTC')
        modified_at = tz.localize(self.modified_at, is_dst=None)
        return {
            'timestamp': modified_at.isoformat(),
            'title': self.title,
            'body': self.body,
        }
