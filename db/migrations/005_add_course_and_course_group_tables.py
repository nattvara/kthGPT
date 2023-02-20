"""Peewee migrations -- 005_add_course_and_course_group_tables.py."""

import peewee as pw
from peewee_migrate import Migrator

from db.models import Course, CourseGroup
from db.database import db


try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    db.create_tables([Course, CourseGroup])


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    db.drop_tables([Course, CourseGroup])
