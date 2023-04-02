"""Peewee migrations -- 013_add_mathpix_requests_table.py."""
import peewee as pw
from peewee_migrate import Migrator

from db.models import MathpixRequest
from db.database import db


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    db.create_tables([MathpixRequest])


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    db.drop_tables([MathpixRequest])
