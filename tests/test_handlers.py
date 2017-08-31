import json
import datetime


import flask
import pytest
from authd import dataaccess, models

email = "test4@mail.com"
password = "123456"


def test_create_user_if_email_is_invalid(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "Invalid",
            "password": "123456"
        }),
        content_type="aplication/json")
    assert resp.status_code == 400


def test_create_user_if_password_is_short(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "test@mail.com",
            "password": "1"
        }),
        content_type="aplication/json")
    assert resp.status_code == 400


def test_create_user_if_missing_email(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "password": "123456"
        }),
        content_type="aplication/json")
    assert resp.status_code == 400


def test_create_user_if_missing_password(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "test@mail.com",
        }),
        content_type="aplication/json")
    assert resp.status_code == 400


def test_create_user_if_missing_email_password(client):
    resp = client.post(
        "/users", data=json.dumps({}), content_type="aplication/json")
    assert resp.status_code == 400


def test_create_user_exists(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "test_exists@mail.com",
            "password": "123456"
        }),
        content_type="aplication/json")
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "test_exists@mail.com",
            "password": "123456"
        }),
        content_type="aplication/json")
    assert resp.status_code == 400


def test_create_user_success(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "test_success@mail.com",
            "password": "123456"
        }),
        content_type="aplication/json")
    assert resp.status_code == 201


def test_confirm_user_if_confirmation_not_exists(client):
    resp = client.get(
        "/actions/invalid_conf_id")
    assert resp.status_code == 404


def test_confirm_user_success(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "test_confirm@mail.com",
            "password": "123456"
        }),
        content_type="aplication/json")
    assert resp.status_code == 201
    conf_id = json.loads(resp.data)["confirmation"]["id"]
    resp = client.get(
        "/actions/{0}".format(conf_id))
    assert resp.status_code == 200
    assert json.loads(resp.data)["user"]["active"]


def test_confirm_user_expired(client, faketime):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "test_expired@mail.com",
            "password": "123456"
        }),
        content_type="aplication/json")
    utc_now = faketime.current_utc
    faketime.current_utc = datetime.datetime(2018, 1, 1, 16, 0, 0)
    assert resp.status_code == 201
    conf_id = json.loads(resp.data)["confirmation"]["id"]
    resp = client.get(
        "/actions/{0}".format(conf_id))
    assert resp.status_code == 400
