"""Peewee migrations -- 003_add_token_usage_table.py."""
# flake8: noqa

import peewee as pw
from peewee_migrate import Migrator

from db.models import TokenUsage
from db.database import db


try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    db.create_tables([TokenUsage])


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    db.drop_tables([TokenUsage])
