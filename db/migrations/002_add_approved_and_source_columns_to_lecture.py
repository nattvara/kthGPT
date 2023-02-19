"""Peewee migrations -- 002_add_approved_and_source_columns_to_lecture.py."""

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
    approved_field = pw.BooleanField(null=True)
    source_field = pw.CharField(null=False, default=Lecture.Source.KTH)
    migrator.add_fields(Lecture, approved=approved_field, source=source_field)
    migrator.run()

    lectures = Lecture.select()
    for lecture in lectures:
        lecture.approved = True
        lecture.save()


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    migrator.remove_fields(Lecture, 'approved', cascade=True)
    migrator.remove_fields(Lecture, 'source', cascade=True)
