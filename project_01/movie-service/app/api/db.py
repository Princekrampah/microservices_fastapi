from sqlalchemy import (Column, Integer, MetaData, String, Table,
                        create_engine, ARRAY)

from databases import Database
from decouple import config

SQLALCHEMY_DATABASE_URL = f'postgresql://{config("DATABASE_USERNAME")}:{config("DATABASE_PASSWORD")}@{config("DATABASE_HOSTNAME")}:{config("DATABASE_PORT")}/{config("DATABASE_NAME")}'


engine = create_engine(SQLALCHEMY_DATABASE_URL)
metadata = MetaData()

movies = Table(
    'movies',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50)),
    Column('plot', String(250)),
    Column('genres', ARRAY(String)),
    Column('casts', ARRAY(String))
)

database = Database(SQLALCHEMY_DATABASE_URL)
