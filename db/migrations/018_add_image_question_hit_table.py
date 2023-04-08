"""Peewee migrations -- 018_add_image_question_hit_table.py."""
import peewee as pw
from peewee_migrate import Migrator

from db.models import ImageQuestionHit
from db.database import db


def migrate(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your migrations here."""
    db.create_tables([ImageQuestionHit])


def rollback(migrator: Migrator, database: pw.Database, fake=False, **kwargs):
    """Write your rollback migrations here."""
    db.drop_tables([ImageQuestionHit])
