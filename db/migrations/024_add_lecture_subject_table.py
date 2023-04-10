"""Peewee migrations -- 024_add_lecture_subject_table.py."""
import peewee as pw
from peewee_migrate import Migrator

from db.models import LectureSubject
from db.database import db


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    db.create_tables([LectureSubject])


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    db.drop_tables([LectureSubject])
