import sqlalchemy as sa
import psycopg2
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    user_id = sa.Column("user_id", UUID, primary_key=True)
    login = sa.Column("login", sa.VARCHAR(16))
    password = sa.Column("password", sa.VARCHAR(24))
    created = sa.Column("created", sa.DateTime)
    active = sa.Column("active", sa.Boolean)


class Confirm(Base):
    __tablename__ = "confirmation"
    conf_id = sa.Column("conf_id", UUID, primary_key=True)
    user_id = sa.Column("user_id", UUID, sa.ForeignKey("users.user_id"))
    conf = sa.Column("conf", sa.Boolean)
    created = sa.Column("created", sa.DateTime)
    expires = sa.Column("expires", sa.DateTime)
