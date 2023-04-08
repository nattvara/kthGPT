"""Peewee migrations -- 019_add_query_hash_column_to_image_question_table.py."""
import peewee as pw
from peewee_migrate import Migrator

from db.models import ImageQuestion


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    field = pw.CharField(index=True, null=True)
    migrator.add_fields(
        ImageQuestion,
        query_hash=field,
    )
    migrator.run()


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    migrator.remove_fields(ImageQuestion, 'query_hash', cascade=True)
