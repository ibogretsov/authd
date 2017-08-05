from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base


# engine = create_engine(
# "postgresql://postgres@localhost:5432/database")


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    user_id = Column("user_id", Integer, primary_key=True)
    login = Column("login", VARCHAR(16))
    password = Column("password", VARCHAR(24))
    created = Column("created", DateTime)


class Confirm(Base):
    __tablename__ = "confirmation"
    conf_id = Column("conf_id", Integer, primary_key=True)
    user_id = Column("user_id", Integer, ForeignKey("users.user_id"))
    conf = Column("conf", Boolean)
