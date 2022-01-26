import json

from datetime import datetime
from peewee import CharField, FloatField, ForeignKeyField
from peewee import Field, IntegerField, DateField, DateTimeField, CharField, ForeignKeyField, Model as PWModel
from peewee import SqliteDatabase
from playhouse.sqlite_ext import JSONField

db = SqliteDatabase('test_melanodb.db')

class Mutations(PWModel):


     class Meta():
        database = db
        table_name = 'mutations'