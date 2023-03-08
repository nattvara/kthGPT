"""Peewee migrations -- 011_add_more_cache_is_valid_column_to_query_table.py."""
import peewee as pw
from peewee_migrate import Migrator

from db.models import Query


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    field = pw.BooleanField(null=False, default=True)
    migrator.add_fields(
        Query,
        cache_is_valid=field,
    )
    migrator.run()


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    migrator.remove_fields(Query, 'cache_is_valid', cascade=True)
