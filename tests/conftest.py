import pytest

from server import create_app


@pytest.fixture
def app(conf):
    app = create_app(conf)
    return app


if __name__ == "__main__":
    app("authd/authdb.json")
