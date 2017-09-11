import datetime

import bcrypt
import voluptuous as schema

from authd import models

USER_SCHEMA = schema.Schema({
    schema.Required("email"):
    schema.Email(),
    schema.Required("password"):
    schema.All(str, schema.Length(min=6))
})


def create_date_time(config):
    now = datetime.datetime.utcnow()
    expires = now + config["security"]["ttl"]
    return now, expires


def email_password_correct(data, abort):
    try:
        USER_SCHEMA(data)
    except schema.MultipleInvalid as e:
        abort(str(e), 400)


class UserManager:
    def __init__(self, config, storage, action_manager):
        self.storage = storage
        self.action_manager = action_manager
        self.config = config

    def create(self, email, password):
        hash_password = bcrypt.hashpw(password,
                                      bcrypt.gensalt()).decode("utf-8")
        if self.storage.users.find(email) is not None:
            raise SecurityError("This user already exists")
        user = models.User(
            email=email,
            password=hash_password,
            created=datetime.datetime.utcnow())
        self.storage.users.create(user)
        confirmation = self.action_manager.create(user)
        self.storage.commit()
        return user, confirmation

    def confirm(self, confirm_id):
        existing = self.action_manager.find(confirm_id)
        if existing is None:
            raise NotFound("Confirmation not exists")
        if existing.expires < datetime.datetime.utcnow():
            confirm_id = self.action_manager.expired(existing)
            raise Expired("Confirmation expired", confirm_id)
        self.storage.actions.delete(existing.confirm_id)
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
        confirmation = models.Confirm(user=user, created=now, expires=expires)
        self.storage.actions.create(confirmation)
        return confirmation

    def find(self, confirm_id):
        return self.storage.actions.find(confirm_id)

    def expired(self, existing):
        self.storage.actions.delete(existing.confirm_id)
        now, expires = create_date_time(self.config)
        confirmation = models.Confirm(
            user_id=existing.user_id, created=now, expires=expires)
        self.storage.actions.create(confirmation)
        self.storage.commit()
        return confirmation.confirm_id


class SecurityError(Exception):
    pass


class Expired(SecurityError):
    def __init__(self, confirm_id, message):
        super(Expired, self).__init__(confirm_id, message)
        self.confirm_id = confirm_id


class NotFound(SecurityError):
    pass


class NotActive(SecurityError):
    pass
