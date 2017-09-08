import contextlib

import lazy
import sqlalchemy as sa
from sqlalchemy import orm
from authd import models


def connect_db(dsn):
    engine = sa.create_engine(dsn)
    session = orm.scoped_session(
        orm.sessionmaker(bind=engine, expire_on_commit=False))
    # read about with operator!!!
    return contextlib.closing(Storage(session))


class UserRepository:
    def __init__(self, session):
        self.session = session

    def create(self, user):
        self.session.add(user)

    def find(self, email):
        return self.session.query(models.User.email).filter(
            models.User.email == email).first()

    def find_user(self, email):
        return self.session.query(models.User.email, models.User.password,
                                  models.User.active).filter(
                                      models.User.email == email).first()

    def update(self, user_id):
        self.session.query(models.User).filter(
            models.User.user_id == user_id).update(
                {
                    models.User.active: True
                }, synchronize_session=False)


class ActionsRepository:
    def __init__(self, session):
        self.session = session

    def create(self, conf):
        self.session.add(conf)

    def find(self, conf_id):
        return self.session.query(models.Confirm).filter(
            models.Confirm.conf_id == str(conf_id)).first()

    def delete(self, conf_id):
        self.session.query(models.Confirm).filter(
            models.Confirm.conf_id == str(conf_id)).delete()


class Storage:
    def __init__(self, session):
        self.session = session

    def commit(self):
        self.session.commit()

    def close(self):
        self.session.close()

    @lazy.lazy
    def users(self):
        return UserRepository(self.session)

    @lazy.lazy
    def actions(self):
        return ActionsRepository(self.session)
