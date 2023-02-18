from peewee_migrate import Router
import sys
import os

from db.database import db
from config.logger import log

MIGRATIONS_DIR = os.path.dirname(os.path.realpath(__file__))

router = Router(db, migrate_dir=MIGRATIONS_DIR, logger=log())


def create_migration():
    router.create(sys.argv[1])


def run_migrations():
    # Run all unapplied migrations
    router.run()


def rollback():
    router.rollback()
