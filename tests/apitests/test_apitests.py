import pytest
from fastapi import status
from fastapi.testclient import TestClient as TC

from users_fastapi.main import app

client = TC(app)
USER_EMAIL, PASSWORD = "user@email.com", "password"


@pytest.mark.usefixtures("repo")
class TestApi:
    def send_auth_form(self, path, user_email, password):
        response = client.post(
            path,
            headers={"Content-type": "application/x-www-form-urlencoded"},
            data=f"grant_type=password&username={user_email}&password={password}",
        )
        return response

    def create_user(self, user_email=USER_EMAIL, password=PASSWORD):
        return self.send_auth_form("/users", user_email, password)

    def auth_user(self, user_email=USER_EMAIL, password=PASSWORD):
        return self.send_auth_form("/token", user_email, password)

    def test_read_main(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "User Microservice"}

    def test_create_user(self):
        # create user
        response = self.create_user()
        user = response.json()
        assert status.HTTP_201_CREATED == response.status_code
        assert user["email"] == USER_EMAIL
        assert user["user_type"] == "CUSTOMER"
        # create duplicated user
        response = self.create_user()
        assert status.HTTP_409_CONFLICT == response.status_code

    def test_get_user(self):
        _ = self.create_user()
        response = self.auth_user(USER_EMAIL, "invalid_password")
        assert status.HTTP_401_UNAUTHORIZED == response.status_code
        response = self.auth_user(USER_EMAIL, PASSWORD)
        access_token = response.json().get("access_token")
        assert access_token is not None
        response = client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})
        assert response is not None
        user = response.json()
        assert USER_EMAIL == user["email"]
        assert "CUSTOMER" == user["user_type"]

    def test_update_user(self):
        new_user_email = "user2@email.com"
        _ = self.create_user()
        _ = self.create_user(new_user_email, PASSWORD)
        access_token = self.auth_user(USER_EMAIL, PASSWORD).json().get("access_token")
        response = client.put(
            "/users",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"field": "email", "value": new_user_email},
        )
        assert status.HTTP_409_CONFLICT == response.status_code
        updated_email = "user@mailB.com"
        response = client.put(
            "/users",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"field": "email", "value": updated_email},
        )
        user = response.json()
        assert updated_email == user["email"]

    def test_delete_user(self):
        _ = self.create_user()
        access_token = self.auth_user(USER_EMAIL, PASSWORD).json().get("access_token")
        response = client.delete("/users", headers={"Authorization": f"Bearer {access_token}"})
        assert status.HTTP_204_NO_CONTENT == response.status_code
        response = client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})
        assert status.HTTP_401_UNAUTHORIZED == response.status_code
