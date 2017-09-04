import json
import datetime

import pytest


@pytest.fixture
def config():
    # read config from etc/authd.json like in server::create_app
    # return cfg
    pass


@pytest.fixture
def session(request, config):
    # return dataaccess.connect_db()
    pass


@pytest.fixture
def credentials(request, session):
    # credentials = {"email": "user@mail.com", "passwrod": "123456"}

    # def fin():
    #     session.query(models.User).delete(
    #         models.User.email == credentials["emdil"])

    # request.addfinalizer(fin)
    # return credentials

    pass


# def test_create_user_seccess_example(client, credentials):
#     resp = client.post(
#         "/users",
#         data=json.dumps(credentials),
#         content_type="application/json")
#     assert resp.status_code == 201


def test_create_user_if_email_is_invalid(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "Invalid",
            "password": "123456"
        }),
        content_type="application/json")
    assert resp.status_code == 400


def test_create_user_if_password_is_short(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "test@mail.com",
            "password": "1"
        }),
        content_type="application/json")
    assert resp.status_code == 400


def test_create_user_if_missing_email(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "password": "123456"
        }),
        content_type="application/json")
    assert resp.status_code == 400


def test_create_user_if_missing_password(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "test@mail.com",
        }),
        content_type="application/json")
    assert resp.status_code == 400


def test_create_user_if_missing_email_password(client):
    resp = client.post(
        "/users", data=json.dumps({}), content_type="application/json")
    assert resp.status_code == 400


def test_create_user_exists(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "test_exists@mail.com",
            "password": "123456"
        }),
        content_type="application/json")
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "test_exists@mail.com",
            "password": "123456"
        }),
        content_type="application/json")
    assert resp.status_code == 400


def test_create_user_success(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "test_success@mail.com",
            "password": "123456"
        }),
        content_type="application/json")
    assert resp.status_code == 201


def test_confirm_user_if_confirmation_not_exists(client):
    resp = client.get("/actions/invalid_conf_id")
    assert resp.status_code == 404


def test_confirm_user_success(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "test_confirm@mail.com",
            "password": "123456"
        }),
        content_type="application/json")
    assert resp.status_code == 201
    conf_id = json.loads(resp.data)["confirmation"]["id"]
    resp = client.get("/actions/{0}".format(conf_id))
    assert resp.status_code == 200
    assert json.loads(resp.data)["user"]["active"]


def test_confirm_user_expired(client, faketime):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "test_expired@mail.com",
            "password": "123456"
        }),
        content_type="application/json")
    assert resp.status_code == 201
    faketime.current_utc = datetime.datetime(2018, 1, 1, 16, 1, 11)
    conf_id = json.loads(resp.data)["confirmation"]["id"]
    resp = client.get("/actions/{0}".format(conf_id))
    assert resp.status_code == 404


def test_login_if_email_invalid(client):
    resp = client.post(
        "/v1/tokens",
        data=json.dumps({
            "email": "Invalid",
            "password": "123456"
        }),
        content_type="application/json")
    assert resp.status_code == 400


def test_login_if_password_short(client):
    resp = client.post(
        "/v1/tokens",
        data=json.dumps({
            "email": "login@mail.com",
            "password": "1"
        }),
        content_type="application/json")
    assert resp.status_code == 400


def test_login_if_missing_email(client):
    resp = client.post(
        "/v1/tokens",
        data=json.dumps({
            "password": "123456"
        }),
        content_type="application/json")
    assert resp.status_code == 400


def test_login_if_missing_password(client):
    resp = client.post(
        "/v1/tokens",
        data=json.dumps({
            "email": "login@mail.com",
        }),
        content_type="application/json")
    assert resp.status_code == 400


def test_login_if_missing_email_password(client):
    resp = client.post(
        "/v1/tokens", data=json.dumps({}), content_type="application/json")
    assert resp.status_code == 400


def test_login_user_not_found(client):
    resp = client.post(
        "/v1/tokens",
        data=json.dumps({
            "email": "login@mail.com",
            "password": "123456"
        }),
        content_type="application/json")
    assert resp.status_code == 401


def test_login_user_not_active(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "login@mail.com",
            "password": "123456"
        }),
        content_type="application/json")
    assert resp.status_code == 201
    resp = client.post(
        "/v1/tokens",
        data=json.dumps({
            "email": "login@mail.com",
            "password": "123456"
        }),
        content_type="application/json")
    assert resp.status_code == 400


def test_login_password_dont_matched(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "login_password@mail.com",
            "password": "123456"
        }),
        content_type="application/json")
    assert resp.status_code == 201
    conf_id = json.loads(resp.data)["confirmation"]["id"]
    resp = client.get("/actions/{0}".format(conf_id))
    assert resp.status_code == 200
    assert json.loads(resp.data)["user"]["active"]
    resp = client.post(
        "/v1/tokens",
        data=json.dumps({
            "email": "login_password@mail.com",
            "password": "123456777"
        }),
        content_type="application/json")
    assert resp.status_code == 401


def test_login_success(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "login_success@mail.com",
            "password": "123456"
        }),
        content_type="application/json")
    assert resp.status_code == 201
    conf_id = json.loads(resp.data)["confirmation"]["id"]
    resp = client.get("/actions/{0}".format(conf_id))
    assert resp.status_code == 200
    assert json.loads(resp.data)["user"]["active"]
    resp = client.post(
        "/v1/tokens",
        data=json.dumps({
            "email": "login_success@mail.com",
            "password": "123456"
        }),
        content_type="application/json")
    assert resp.status_code == 200
