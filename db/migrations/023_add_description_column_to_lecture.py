"""Peewee migrations -- 023_add_description_column_to_lecture.py."""
import peewee as pw
from peewee_migrate import Migrator

from db.models import Lecture


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    field = pw.TextField(null=True)
    migrator.add_fields(
        Lecture,
        description=field,
    )
    migrator.run()


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    migrator.remove_fields(Lecture, 'description', cascade=True)
