import datetime


import bcrypt

from authd import models


def create_date_time(config):
    now = datetime.datetime.utcnow()
    expires = now + config["security"]["ttl"]
    return now, expires


class UserManager:
    def __init__(self, storage, actions_manager, config):
        self.storage = storage
        self.actions_manager = actions_manager
        self.config = config

    def create(self, email, password):
        if self.storage.users.find(email) is not None:
            raise SecurityError("This user already exists")
        user = models.User(
            email=email,
            password=bcrypt.hashpw(password, bcrypt.gensalt()),
            created=datetime.datetime.utcnow())
        self.storage.users.create(user)
        conf = self.actions_manager.create(user)
        self.storage.commit()
        return user, conf

    def update(self, user_id):
        self.storage.users.update(user_id)
        self.storage.commit()

    def login(self, email, password):
        user = self.storage.users.find_user(email)
        if user is None:
            raise SecurityError("User isn't found")
        if not user.active:
            raise SecurityError("User isn't active")
        hash_pass = user.password.encode("utf-8")
        data_pass = password.encode("utf-8")
        if not bcrypt.checkpw(data_pass, hash_pass):
            raise SecurityError("Password doesn't match")
        return user.email, user.password


class ActionsManager:
    def __init__(self, storage, config):
        self.storage = storage
        self.config = config

    def create(self, user):
        now, expires = create_date_time(self.config)
        conf = models.Confirm(
            user=user,
            created=now,
            expires=expires)
        self.storage.actions.create(conf)
        return conf

    def expired(self, conf_id):
        existing = self.storage.actions.find(conf_id)
        if existing is None:
            raise SecurityError("Confirmation not exists")
        if existing.expires < datetime.datetime.utcnow():
            self.delete(conf_id)
            now, expires = create_date_time(self.config)
            conf = models.Confirm(
                user_id=existing.user_id, created=now, expires=expires)
            self.storage.actions.create(conf)
            self.storage.commit()
            return conf.conf_id

    def delete(self, conf_id):
        self.storage.actions.delete()


class SecurityError(Exception):
    pass
