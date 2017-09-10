import datetime

import bcrypt

from authd import models


def create_date_time(config):
    now = datetime.datetime.utcnow()
    expires = now + config["security"]["ttl"]
    return now, expires


class UserManager:
    def __init__(self, config, storage, action_manager):
        self.storage = storage
        self.action_manager = action_manager
        self.config = config

    def create(self, email, password):
        if self.storage.users.find(email) is not None:
            raise SecurityError("This user already exists")
        user = models.User(
            email=email, password=password, created=datetime.datetime.utcnow())
        self.storage.users.create(user)
        confirmation = self.action_manager.create(user)
        self.storage.commit()
        return user, confirmation

    def confirm(self, conf_id):
        existing = self.action_manager.find(conf_id)
        if existing is None:
            raise NotFound("Confirmation not exists")
        if existing.expires < datetime.datetime.utcnow():
            conf_id = self.action_manager.expired(existing)
            raise Expired("Confirmation expired", conf_id)
        self.storage.actions.delete(existing.conf_id)
        self.storage.users.update(existing.user_id, {models.User.active: True})
        self.storage.commit()
        return existing.user_id

    def login(self, email, password):
        user = self.storage.users.find_user(email)
        if user is None:
            raise NotFound("User isn't found")
        if not user.active:
            raise NotActive("User isn't active")
        hash_pass = user.password.encode("utf-8")
        data_pass = password.encode("utf-8")
        if not bcrypt.checkpw(data_pass, hash_pass):
            raise SecurityError("Password doesn't match")


class ActionManager:
    def __init__(self, config, storage):
        self.storage = storage
        self.config = config

    def create(self, user):
        now, expires = create_date_time(self.config)
        conf = models.Confirm(user=user, created=now, expires=expires)
        self.storage.actions.create(conf)
        return conf

    def find(self, conf_id):
        return self.storage.actions.find(conf_id)

    def expired(self, existing):
        self.storage.actions.delete(existing.conf_id)
        now, expires = create_date_time(self.config)
        conf = models.Confirm(
            user_id=existing.user_id, created=now, expires=expires)
        self.storage.actions.create(conf)
        self.storage.commit()
        return conf.conf_id


class SecurityError(Exception):
    pass


class Expired(SecurityError):
    def __init__(self, conf_id, message):
        super(Expired, self).__init__(conf_id, message)
        self.conf_id = conf_id


class NotFound(SecurityError):
    pass


class NotActive(SecurityError):
    pass