import datetime
from unittest import mock

import pytest
from server import create_app


@pytest.fixture
def app():
    app = create_app("etc/authdb.json")
    return app


# -*- coding:utf-8 -*-
"""pytest-faketime plugin.
"""


@pytest.fixture
def faketime(request):

    class FakeTime(datetime.datetime):

        current = datetime.datetime.now()
        current_utc = datetime.datetime.utcnow()

        @classmethod
        def now(cls):
            return cls.current

        @classmethod
        def utcnow(cls):
            return cls.current_utc

    datetime_mock = mock.patch("datetime.datetime", new=FakeTime)
    datetime_mock.start()
    request.addfinalizer(datetime_mock.stop)
    return datetime.datetime
