"""Peewee migrations -- 002_add_approved_column_to_urls.py."""

import peewee as pw
from peewee_migrate import Migrator

from db.models import URL

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    new_field = pw.BooleanField(null=True)
    migrator.add_fields(URL, approved=new_field)
    migrator.run()

    urls = URL.select()
    for url in urls:
        url.approved = True
        url.save()


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    migrator.remove_fields(URL, 'approved', cascade=True)
