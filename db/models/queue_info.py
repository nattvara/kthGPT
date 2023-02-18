import peewee

from .base import Base


class QueueInfo(Base):
    # Queues
    queue_default = peewee.IntegerField(null=False, default=0)
    queue_summarise = peewee.IntegerField(null=False, default=0)
    queue_transcribe = peewee.IntegerField(null=False, default=0)
    queue_extract = peewee.IntegerField(null=False, default=0)
    queue_download = peewee.IntegerField(null=False, default=0)
    queue_monitoring = peewee.IntegerField(null=False, default=0)

    workers = peewee.TextField(null=False)
