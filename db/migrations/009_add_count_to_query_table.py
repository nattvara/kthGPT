"""Peewee migrations -- 009_add_count_to_query_table.py."""

import peewee as pw
from peewee_migrate import Migrator

from db.models import Query

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    field = pw.IntegerField(null=False, default=0)

    migrator.add_fields(Query, count=field)
    migrator.run()


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    migrator.remove_fields(Query, 'count', cascade=True)
