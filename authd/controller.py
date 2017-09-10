import lazy


from authd import dataaccess, managers


class Container:
    def __init__(self, conf):
        self.conf = conf
        self.storage = None

    def __enter__(self):
        self.storage = dataaccess.connect_db(self.conf["database"]["DSN"])
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.storage.close()

    @lazy.lazy
    def user_manager(self):
        return managers.UserManager(
            self.conf,
            self.storage,
            self.action_manager)

    @lazy.lazy
    def action_manager(self):
        return managers.ActionManager(
            self.conf,
            self.storage)


class Controller:
    def __init__(self, conf):
        self.conf = conf

    def create_user(self, email, password):
        with Container(self.conf) as container:
            user, confirmation = container.user_manager.create(
                email, password)
        return user, confirmation

    def confirm_user(self, confirm_id):
        with Container(self.conf) as container:
            user_id = container.user_manager.confirm(confirm_id)
        return user_id

    def login(self, email, password):
        with Container(self.conf) as container:
            container.user_manager.login(email, password)
        return email, password
