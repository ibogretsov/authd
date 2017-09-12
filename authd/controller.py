import lazy


from authd import dataaccess, managers


class Container:
    def __init__(self, config):
        self.config = config
        self.storage = None

    def __enter__(self):
        self.storage = dataaccess.connect_db(self.config["database"]["DSN"])
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.storage.close()

    @lazy.lazy
    def user_manager(self):
        return managers.UserManager(
            self.config,
            self.storage,
            self.action_manager)

    @lazy.lazy
    def action_manager(self):
        return managers.ActionManager(
            self.config,
            self.storage)


class Controller:
    def __init__(self, config):
        self.config = config

    def create_user(self, email, password):
        with Container(self.config) as container:
            user, confirmation = container.user_manager.create(
                email, password)
        return user, confirmation

    def confirm_user(self, confirm_id):
        with Container(self.config) as container:
            user_id = container.user_manager.confirm(confirm_id)
        return user_id

    def login(self, email, password):
        with Container(self.config) as container:
            container.user_manager.login(email, password)
        return email, password

    def request_password_reset(self, email):
        with Container(self.config) as container:
            confirmation = container.user_manager.request_password_reset(email)
        return confirmation

    def reset_password(self, confirm_id, password):
        with Container(self.config) as container:
            container.user_manager.reset_password(confirm_id, password)
