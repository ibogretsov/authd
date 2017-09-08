import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    user_id = sa.Column(
        "user_id",
        pg.UUID,
        server_default=sa.text("gen_random_uuid()"),
        primary_key=True)
    email = sa.Column(
        "email", sa.VARCHAR(128), index=True, unique=True, nullable=False)
    password = sa.Column("password", sa.VARCHAR(128), nullable=False)
    created = sa.Column("created", sa.DateTime, nullable=False)
    active = sa.Column("active", sa.Boolean, nullable=False, default=False)


class Confirm(Base):
    __tablename__ = "confirmation"
    conf_id = sa.Column(
        "conf_id",
        pg.UUID,
        server_default=sa.text("gen_random_uuid()"),
        primary_key=True)
    user_id = sa.Column(
        "user_id",
        pg.UUID,
        sa.ForeignKey("users.user_id", ondelete='CASCADE'),
        nullable=False)
    created = sa.Column("created", sa.DateTime, nullable=False)
    expires = sa.Column("expires", sa.DateTime, nullable=False)
    user = relationship("User")
