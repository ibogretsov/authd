import contextlib


import sqlalchemy as sa
from sqlalchemy import orm


def connect_db(dsn):
    engine = sa.create_engine(dsn)
    session = orm.scoped_session(orm.sessionmaker(bind=engine, expire_on_commit=False))
    return contextlib.closing(session)
