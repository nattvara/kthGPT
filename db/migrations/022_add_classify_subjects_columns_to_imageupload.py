"""Peewee migrations -- 022_add_classify_subjects_columns_to_imageupload.py."""
import peewee as pw
from peewee_migrate import Migrator

from db.models import ImageUpload


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    classify_subjects_ok = pw.BooleanField(null=True)
    classify_subjects_failure_reason = pw.TextField(null=True)

    migrator.add_fields(
        ImageUpload,
        classify_subjects_ok=classify_subjects_ok,
        classify_subjects_failure_reason=classify_subjects_failure_reason,
    )
    migrator.run()


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    migrator.remove_fields(ImageUpload, 'classify_subjects_ok', cascade=True)
    migrator.remove_fields(ImageUpload, 'classify_subjects_failure_reason', cascade=True)
