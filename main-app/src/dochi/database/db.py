"""
db.py

Export database
"""

import os
from peewee import SqliteDatabase


db = SqliteDatabase(os.environ["DATABASE_PATH"])
