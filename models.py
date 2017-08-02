from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2


engine = create_engine(
    "postgresql+psycopg2://postgres@localhost:5432/database")


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)

    def __repr__(self):
        return "User<(user_id={0},login={1}, password={2})>".\
            format(self.user_id, self.login, self.password)


class Confirm(Base):
    __tablename__ = "confirmation"
    conf_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    conf = Column(Boolean)

    def __repr__(self):
        return "Confirm<(conf_id={0}, user_id={1}, conf={2})>".\
            format(self.conf_id, self.user_id, self.conf)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
session.add(User(login='testtest', password='1'))
session.add_all([User(login="ilya", password="12345"),
                 User(login="vova", password="qwerty"),
                 User(login="test", password="1"),
                 User(login="asd", password="asd"),
                 Confirm(user_id=1, conf=False),
                 Confirm(user_id=2, conf=True),
                 Confirm(user_id=3, conf=False),
                 Confirm(user_id=4, conf=True),
                 Confirm(user_id=5, conf=False)])
session.commit()
