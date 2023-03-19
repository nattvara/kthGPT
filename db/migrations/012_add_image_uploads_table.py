"""Peewee migrations -- 012_add_image_uploads_table.py."""
import peewee as pw
from peewee_migrate import Migrator

from db.models import ImageUpload
from db.database import db


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    db.create_tables([ImageUpload])


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    db.drop_tables([ImageUpload])
