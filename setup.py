import distutils.cmd
import distutils.log
import setuptools
import os

import sqlalchemy
import sqlalchemy_utils


def crt_engine(user, password):
    """create engine"""
    if user is not None and password is not None:
        engine = sqlalchemy.create_engine(
            "postgresql://{0}:{1}@localhost:5432/database".
            format(user, password))
    elif user is not None:
        engine = sqlalchemy.create_engine(
            "postgresql://{0}@localhost:5432/database".
            format(user))
    else:
        engine = sqlalchemy.create_engine(
            "postgresql://localhost:5432/database")
    return engine


class DatabaseCommand(distutils.cmd.Command):
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


class CreateDatabase(DatabaseCommand):
    """A custom command to create Database"""

    def run(self):
        """Run command"""
        engine = crt_engine(self.database_user, self.database_password)
        if not sqlalchemy_utils.database_exists(engine.url):
            sqlalchemy_utils.functions.create_database(engine.url)


class DropDatabase(DatabaseCommand):
    """A custom command to delete Database"""

    def run(self):
        """Run command"""
        engine = crt_engine(self.database_user, self.database_password)
        if sqlalchemy_utils.database_exists(engine.url):
            sqlalchemy_utils.functions.drop_database(engine.url)


class DBSync(distutils.cmd.Command):
    """A custom command to run alembic"""

    description = "run alembic"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run command"""
        os.system("alembic upgrade head")


setuptools.setup(
    cmdclass={"createdb": CreateDatabase,
              "dropdb": DropDatabase,
              "dbsync": DBSync},
    name="authd",
    packages=["authd"],
    version="0.1.0",
    author="ilyabogretsov",
    author_email="ilyabogrecov@gmail.com",
    url="https://gitlab.com/ilyabogrecov/authd",
    keywords=["authentication", "users"],
)
