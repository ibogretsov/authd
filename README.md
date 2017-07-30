# authd

Authentication service for study purposes written in [flask](http://flask.pocoo.org).
Database access should be implmeneted using [sqlalchemy](https://www.sqlalchemy.org) ORM.

## Repository layout

```
/
├── authd/                          # authd package folder.
├────── __init__.py
├────── dataaccess.py               # Database operations functions. (optional)
├────── models.py                   # SQL Alchemy models definitions.
├────── migrations.py               # SQL Alchemy migrations.
├────── handlers.py                 # Flask HTTP handlers.
├── test/
├────── test_dataaccess.py          # Database operations tests. (optional)
├────── test_handlers.py            # HTTP handlers tests.
├── .gitignore
├── README.md
├── LICENSE
├── TODO
├── setup.py
├── setup.cfg (optional)
```

## Tests

Tests should be implemented in [pytest](https://docs.pytest.org/en/latest/).

## API

### Create user

```
    POST /users HTTP/1.1
    Content-Type: application/json; charset=UTF-8
    {
        "email": "test-user-1@mail.com",
        "password": "123456"
    }
```

* email is required, should match email pattern
* password is required, should be not shorter than 6 chars

Response:

```
    HTTP/1.1 201 Created
    Content-Type: application/json; charset=UTF-8

    {
        "user":
        {
            "id": "e832f45a-6faa-4eb4-8c40-7ad30ab93df8",
            "email": "test-user-1@mail.com",
            "active: false
        },
        "confirmation:
        {
            "id": "2882c253-74f1-4304-b82c-47c8697cf959",
            "created": "2017-01-01 00:00:00"
            "expires": "2017-01-01 00:10:00"
        }
    }
```

Error codes:

* 400 - if user already exists or if user properties do not match requirements

### Confirm user

```
    POST /actions/2882c253-74f1-4304-b82c-47c8697cf959 HTTP/1.1
```

Response:

```
    HTTP/1.1 20O OK
    Content-Type: application/json; charset=UTF-8

    {
        "access_token": "some-access-token"
    }
```

Error codes:

* 404 - if action with id provided does not exists
* 400 - if confirmation has been expired

### Generate token

```
    POST /v1/tokens/ HTTP/1.1
    Content-Type: application/json; charset=UTF-8

    {
        "email": "test-user-1@mail.com"
        "password": "123456"
    }
```

Response:

```
    HTTP/1.1 200 OK
    Content-Type: application/json; charset=UTF-8

    {
        "access_token": "some-access-token"
    }
```

* 401 - user not exists or the password is incorrect