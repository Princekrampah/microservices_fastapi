import os

from sqlalchemy import (Column, Integer, MetaData, String, Table,
                        create_engine, ARRAY)

from databases import Database
from decouple import config
import os

SQLALCHEMY_DATABASE_URL = f'postgresql://{config("DATABASE_USERNAME", default=os.environ.get("DATABASE_USERNAME"))}:{config("DATABASE_PASSWORD", default=os.environ.get("DATABASE_PASSWORD"))}@{config("DATABASE_HOSTNAME", default=os.environ.get("DATABASE_HOSTNAME"))}:{config("DATABASE_PORT", default=os.environ.get("DATABASE_PORT"))}/{config("DATABASE_NAME", default=os.environ.get("DATABASE_NAME"))}'


engine = create_engine(SQLALCHEMY_DATABASE_URL)
metadata = MetaData()

casts = Table(
    'casts',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50)),
    Column('nationality', String(20)),
)

database = Database(SQLALCHEMY_DATABASE_URL)