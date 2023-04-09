"""Peewee migrations -- 020_add_title_to_imageupload.py."""
import peewee as pw
from peewee_migrate import Migrator

from db.models import ImageUpload


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    title = pw.CharField(null=True)
    create_title_ok = pw.BooleanField(null=True)
    create_title_failure_reason = pw.TextField(null=True)

    migrator.add_fields(
        ImageUpload,
        title=title,
        create_title_ok=create_title_ok,
        create_title_failure_reason=create_title_failure_reason,
    )
    migrator.run()


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    migrator.remove_fields(ImageUpload, 'title', cascade=True)
    migrator.remove_fields(ImageUpload, 'create_title_ok', cascade=True)
    migrator.remove_fields(ImageUpload, 'create_title_failure_reason', cascade=True)
