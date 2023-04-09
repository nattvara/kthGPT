"""Peewee migrations -- 021_add_image_upload_subject_table.py."""
import peewee as pw
from peewee_migrate import Migrator

from db.models import ImageUploadSubject
from db.database import db


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    db.create_tables([ImageUploadSubject])


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    db.drop_tables([ImageUploadSubject])
