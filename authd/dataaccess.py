import lazy
import sqlalchemy as sa
from sqlalchemy import orm
from authd import models


def connect_db(dsn):
    engine = sa.create_engine(dsn)
    session = orm.scoped_session(
        orm.sessionmaker(bind=engine, expire_on_commit=False))
    return Storage(session)


class UserRepository:
    def __init__(self, session):
        self.session = session

    def create(self, user):
        self.session.add(user)

    def find(self, email):
        return self.session.query(models.User.email).filter(
            models.User.email == email).first()

    def find_user(self, email):
        return self.session.query(models.User).filter(
            models.User.email == email).first()

    def update(self, user_id, data):
        self.session.query(models.User).filter(
            models.User.user_id == user_id).update(
                data, synchronize_session=False)


class ActionRepository:
    def __init__(self, session):
        self.session = session

    def create(self, confirmation):
        self.session.add(confirmation)

    def find(self, confirm_id):
        return self.session.query(models.Confirm).filter(
            models.Confirm.confirm_id == str(confirm_id)).first()

    def delete(self, confirm_id):
        self.session.query(models.Confirm).filter(
            models.Confirm.confirm_id == str(confirm_id)).delete()


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
        return ActionRepository(self.session)
