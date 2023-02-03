# Users micro-service
Sample project to create a micro-service to manage users based on Fast-API and Postgres.

The core functionalities include:
- CRUD
    - creating a user
    - retrieving a user
    - retireving multiple users
    - changing the user's email
    - deleting the user

- Authentication
    - Bearer token model to authenticate users
    - Users can be of type: Customers, Admins (TODO: defined by realm)
    - Tokens are obtained by submitting a valid email, password form

- Tests
    - Unit tests using tox-docker
    - Integration tests using tox-docker and HTTPX client from Fast-API

For more detail in using tox-docker see:
    - https://betterprogramming.pub/how-to-test-external-dependencies-with-pytest-docker-and-tox-2db0b2e87cde
    - https://github.com/vrgsdaniel/testing-containers

## Start

Run `make start` to launch an uvicorn server on port 8080.
To make requests to the server you can look at the integration tests, or go to `http://localhost:8080/docs`

Run `make test` to run the test suite