import json

import flask
# import pytest
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


def test_user_create_exists(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "test10@mail.com",
            "password": "123456"
        }),
        content_type="aplication/json")
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "test10@mail.com",
            "password": "123456"
        }),
        content_type="aplication/json")
    assert resp.status_code == 400


def test_user_create_ok(client):
    resp = client.post(
        "/users",
        data=json.dumps({
            "email": "test_ok@mail.com",
            "password": "123456"
        }),
        content_type="aplication/json")
    assert resp.status_code == 201
    