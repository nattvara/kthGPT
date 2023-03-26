"""Peewee migrations -- 014_add_upload_id_column_to_token_usage.py."""
import peewee as pw
from peewee_migrate import Migrator

from db.models import TokenUsage


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    field = pw.IntegerField(null=True, index=True)
    migrator.add_fields(
        TokenUsage,
        upload_id=field,
    )
    migrator.run()


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    migrator.remove_fields(TokenUsage, 'upload_id', cascade=True)
