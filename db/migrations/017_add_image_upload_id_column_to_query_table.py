"""Peewee migrations -- 017_add_image_upload_id_column_to_query_table.py."""
import peewee as pw
from peewee_migrate import Migrator

from db.models import Query, Lecture, ImageUpload


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    image_upload_id = pw.ForeignKeyField(ImageUpload, null=True, backref='imageupload', on_delete='cascade')

    migrator.add_fields(
        Query,
        image_upload_id=image_upload_id,
    )
    migrator.sql('ALTER TABLE query ALTER COLUMN lecture_id DROP NOT NULL;')
    migrator.run()


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    migrator.sql('ALTER TABLE query ALTER COLUMN lecture_id TEXT NOT NULL;')
    migrator.remove_fields(Query, 'image_upload_id', cascade=True)
