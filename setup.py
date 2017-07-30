import distutils.cmd
import distutils.log
import setuptools

import sqlalchemy
import sqlalchemy_utils


def create_engine_url(user, password):
    """create engine URL"""
    if user is not None and password is not None:
        engine = sqlalchemy.create_engine(
            "postgresql+psycopg2://{0}:{1}@localhost:5432/database".
            format(user, password))
    elif user is not None:
        engine = sqlalchemy.create_engine(
            "postgresql+psycopg2://{0}@localhost:5432/database".
            format(user))
    else:
        engine = sqlalchemy.create_engine(
            "postgresql+psycopg2://localhost:5432/database")
    return engine.url


class CommandDatabase(distutils.cmd.Command):
    """A custom command to run Database on all Python source files."""
    description = "set user, password for Database in authd"
    user_options = [("database-user=", None, "Database superuser"),
                    ("database-password=", None, "superuser's password")]

    def initialize_options(self):
        """Set dafault values user, password"""
        self.database_user = None
        self.database_password = None

    def finalize_options(self):
        pass


class CreateDatabase(CommandDatabase):
    """A custom command to create Database"""

    def run(self):
        """Run command"""
        url = create_engine_url(self.database_user, self.database_password)
        if not sqlalchemy_utils.database_exists(url):
            sqlalchemy_utils.functions.create_database(url)


class DropDatabase(CommandDatabase):
    """A custom command to delete Database"""

    def run(self):
        """Run command"""
        url = create_engine_url(self.database_user, self.database_password)
        if sqlalchemy_utils.database_exists(url):
            sqlalchemy_utils.functions.drop_database(url)


setuptools.setup(
    cmdclass={"create_database": CreateDatabase,
              "drop_database": DropDatabase},
    name="authd",
    packages=["authd"],
    version="0.1.0",
    author="ilyabogretsov",
    author_email="ilyabogrecov@gmail.com",
    url="https://gitlab.com/ilyabogrecov/authd",
    keywords=["authentication", "users"],
)
