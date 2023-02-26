"""Peewee migrations -- 007_add_small_preview_to_lectures_table.py."""

import peewee as pw
from peewee_migrate import Migrator

from db.models import Lecture

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    field = pw.CharField(null=True)

    migrator.add_fields(Lecture, img_preview_small=field)
    migrator.run()


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    migrator.remove_fields(Lecture, 'img_preview_small', cascade=True)
