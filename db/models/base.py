from datetime import datetime
import peewee

from db.database import db


class Base(peewee.Model):
    created_at = peewee.TimestampField(default=datetime.utcnow, null=False)
    modified_at = peewee.TimestampField(default=datetime.utcnow, null=False)

    class Meta:
        database = db

    class Config:
        orm_mode = True

    def save(self, *args, **kwargs):
        self.modified_at = datetime.utcnow()
        return super(Base, self).save(*args, **kwargs)
