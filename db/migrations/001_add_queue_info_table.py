"""Peewee migrations -- 001_add_queue_info_table.py."""

import peewee as pw
from peewee_migrate import Migrator
from decimal import ROUND_HALF_EVEN

from db.models import QueueInfo
from db.database import db


try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    db.create_tables([QueueInfo])


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    db.drop_tables([QueueInfo])
