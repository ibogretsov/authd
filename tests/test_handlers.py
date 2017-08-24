import json


def test_create_user_if_email_is_invalid(client):
    resp = client.post("/users", data=json.dumps({
        "email": "invalid",
        "password": "123456"
    }))
    assert resp.status_code == 400
