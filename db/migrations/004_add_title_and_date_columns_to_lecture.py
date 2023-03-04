"""Peewee migrations -- 004_add_title_and_date_columns_to_lecture.py."""
# flake8: noqa

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
    title_field = pw.CharField(null=True)
    date_field = pw.TimestampField(null=True)

    migrator.add_fields(Lecture, title=title_field, date=date_field)
    migrator.run()


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    migrator.remove_fields(Lecture, 'title', cascade=True)
    migrator.remove_fields(Lecture, 'date', cascade=True)
