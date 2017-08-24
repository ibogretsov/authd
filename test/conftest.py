import pytest

from server import create_app


@pytest.fixture
def app():
    app = create_app("authd/authdb.json")
    return app
