"""Peewee migrations -- 016_add_group_column_to_lecture_table.py."""
import peewee as pw
from peewee_migrate import Migrator

from db.models import Lecture


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    field = pw.CharField(null=True)
    migrator.add_fields(
        Lecture,
        group=field,
    )
    migrator.run()


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    migrator.remove_fields(Lecture, 'group', cascade=True)
