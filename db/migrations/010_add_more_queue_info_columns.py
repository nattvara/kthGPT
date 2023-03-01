"""Peewee migrations -- 010_add_more_queue_info_columns.py."""

import peewee as pw
from peewee_migrate import Migrator

from db.models import QueueInfo

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    queue_approval_field = pw.IntegerField(null=False, default=0)
    queue_metadata_field = pw.IntegerField(null=False, default=0)
    queue_gpt_field = pw.IntegerField(null=False, default=0)

    migrator.add_fields(
        QueueInfo,
        queue_approval=queue_approval_field,
        queue_metadata=queue_metadata_field,
        queue_gpt=queue_gpt_field,
    )
    migrator.run()


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    migrator.remove_fields(QueueInfo, 'queue_approval', cascade=True)
    migrator.remove_fields(QueueInfo, 'queue_metadata', cascade=True)
    migrator.remove_fields(QueueInfo, 'queue_gpt', cascade=True)
