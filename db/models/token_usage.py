import peewee

from .base import Base


class TokenUsage(Base):
    # not sure how to make this a foreign key field, due to circular imports
    analysis_id = peewee.IntegerField(null=True, index=True)
    query_id = peewee.IntegerField(null=True, index=True)
    upload_id = peewee.IntegerField(null=True, index=True)

    completion_tokens = peewee.IntegerField(null=False, default=0)
    prompt_tokens = peewee.IntegerField(null=False, default=0)
    total_tokens = peewee.IntegerField(null=False, default=0)
