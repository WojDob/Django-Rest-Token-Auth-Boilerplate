import json

from django.contrib.auth import authenticate, get_user, get_user_model
from django.test import TestCase
from knox.models import AuthToken
from rest_framework.test import APIClient


class TestLoginEndpoint(TestCase):
    endpoint = "/api/auth/login/"

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "example", "a@example.com", "pass"
        )
        self.user.save()

    def test_should_login_with_valid_credentials(self):
        response = self.client.post(
            self.endpoint, data={"username": "example", "password": "pass"}
        )

        assert response.status_code == 200
        assert get_user(self.client).is_authenticated

    def test_should_not_login_with_invalid_credentials(self):
        response = self.client.post(
            self.endpoint, data={"username": "example", "password": "wrong"}
        )

        assert response.status_code == 400
        assert not get_user(self.client).is_authenticated

    def test_should_not_login_with_no_credentials(self):
        response = self.client.post(self.endpoint, data={})

        assert response.status_code == 400
        assert not get_user(self.client).is_authenticated

    def test_should_not_login_with_missing_username(self):
        response = self.client.post(self.endpoint, data={"password": "pass"})

        assert response.status_code == 400
        assert not get_user(self.client).is_authenticated

    def test_should_not_login_with_missing_password(self):
        response = self.client.post(self.endpoint, data={"username": "example"})

        assert response.status_code == 400
        assert not get_user(self.client).is_authenticated

    def test_should_return_auth_token_when_login_successfully(self):
        response = self.client.post(
            self.endpoint, data={"username": "example", "password": "pass"}
        )

        assert response.status_code == 200
        assert "token" in response.json()


class TestRegisterEndpoint(TestCase):
    endpoint = "/api/auth/register/"
    valid_register_data = {
        "username": "example",
        "email": "example@example.com",
        "password": "blue-orca",
    }

    def test_should_register(self):
        response = self.client.post(self.endpoint, data=self.valid_register_data)

        assert response.status_code == 201
        assert (
            get_user_model()
            .objects.filter(username=self.valid_register_data["username"])
            .exists()
        )
        assert get_user(self.client).is_authenticated
        assert get_user_model().objects.count() == 1

    def test_should_not_register_with_invalid_email(self):
        response = self.client.post(
            self.endpoint,
            data={
                "username": "example",
                "email": "exampleexample.com",
                "password": "blue-orca",
            },
        )

        assert response.status_code == 400
        assert not get_user_model().objects.filter(username="example").exists()
        assert get_user_model().objects.count() == 0

    def test_should_not_register_if_email_already_exists(self):
        valid_email = self.valid_register_data["email"]

        get_user_model().objects.create_user(valid_email, valid_email, "12345")
        response = self.client.post(self.endpoint, data=self.valid_register_data)

        assert response.status_code == 400
        assert get_user_model().objects.filter(username=valid_email).count() == 1
        assert get_user_model().objects.count() == 1

    def test_should_not_register_if_username_already_exists(self):
        valid_username = self.valid_register_data["username"]

        get_user_model().objects.create_user(
            valid_username, "a@example.com", "oioi12345"
        )
        response = self.client.post(self.endpoint, data=self.valid_register_data)

        assert response.status_code == 400
        assert get_user_model().objects.filter(username=valid_username).count() == 1
        assert get_user_model().objects.count() == 1

    def should_not_register_when_bad_password(self):
        valid_username = self.valid_register_data["username"]
        valid_email = self.valid_register_data["email"]
        response = self.client.post(
            self.endpoint,
            data={
                "username": "example",
                "email": "example@example.com",
                "password": "123",
            },
        )
        assert response.status_code == 400
        assert get_user_model().objects.count() == 0


class TestChangePasswordEndpoint(TestCase):
    endpoint = "/api/auth/change-password/"

    def setUp(self):
        user = get_user_model().objects.create_user("example", "a@example.com", "pass")
        self.client.login(username="example", password="pass")

    def test_change_password_successfully(self):
        response = self.client.put(
            self.endpoint,
            data={"old_password": "pass", "new_password": "newPassword1234"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert authenticate(username="example", password="newPassword1234")
        assert not authenticate(username="example", password="pass")

    def test_wrong_old_password(self):
        response = self.client.put(
            self.endpoint,
            data={"old_password": "wrongPassword", "new_password": "newPassword1234"},
            content_type="application/json",
        )
        assert response.status_code == 400
        assert not authenticate(username="example", password="newPassword1234")
        assert authenticate(username="example", password="pass")

    def test_wrong_data_format(self):
        response = self.client.put(
            self.endpoint,
            data={"wrongData": "123", "oldpassword": "321"},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_should_validate_new_password(self):
        response = self.client.put(
            self.endpoint,
            data={"old_password": "pass", "new_password": "xd"},
            content_type="application/json",
        )
        assert response.status_code == 400
        assert json.loads(response.content) == {
            "new_password": [
                "This password is too short. It must contain at least 8 characters."
            ]
        }

        assert not authenticate(username="example", password="xd")
        assert authenticate(username="example", password="pass")


class TestProfileEndpoint(TestCase):
    endpoint = "/api/auth/profile/"

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "example", "a@example.com", "pass"
        )
        self.token = AuthToken.objects.create(user=self.user)[1]
        self.client = APIClient()

    def test_should_show_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(self.endpoint)

        assert response.status_code == 200
        response_json = json.loads(response.content)
        assert response_json["username"] == self.user.get_username()
        assert response_json["email"] == self.user.email
        assert str(response_json["date_joined"]) == str(self.user.date_joined.date())

    def test_should_not_show_profile_when_not_logged_in(self):
        self.client.credentials()  # Clear any existing credentials
        response = self.client.get(self.endpoint)

        assert response.status_code == 403
