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
    queue_approval = peewee.IntegerField(null=False, default=0)
    queue_metadata = peewee.IntegerField(null=False, default=0)
    queue_gpt = peewee.IntegerField(null=False, default=0)

    workers_idle = peewee.IntegerField(null=False, default=0)
    workers_busy = peewee.IntegerField(null=False, default=0)
