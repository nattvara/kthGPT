"""Peewee migrations -- 008_add_raw_content_link_column.py."""

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

    migrator.add_fields(Lecture, raw_content_link=field)
    migrator.run()


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    migrator.remove_fields(Lecture, 'raw_content_link', cascade=True)
