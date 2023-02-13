from datetime import datetime
import peewee

from db.database import db


class Base(peewee.Model):
    created_at = peewee.DateTimeField(default=datetime.now, null=False)
    modified_at = peewee.DateTimeField(default=datetime.now, null=False)

    class Meta:
        database = db

    class Config:
        orm_mode = True

    def save(self, *args, **kwargs):
        self.modified_at = datetime.now()
        return super(Base, self).save(*args, **kwargs)
