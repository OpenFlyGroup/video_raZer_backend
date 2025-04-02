from os import makedirs, path, remove

from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User

RESP = settings.RESPONSES
max_id = 0


class TestUtils:
    USER_DATA = {
        "email": "test@test.test",
        "password": "test",
        "name": "test",
    }

    def signin(self, email: str, password: str) -> HttpResponse:
        signin_url = reverse(viewname="sign-in")
        data = {"email": email, "password": password}
        return self.client.post(path=signin_url, data=data, format="json")

    def signup_brand(self, email: str, password: str) -> HttpResponse:
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            data = {"email": email, "password": password, "name": "test"}
            User().create_user(
                email=email, password=password, name="name", role="brand"
            )
            signin_url = reverse(viewname="sign-in")
            signin = self.client.post(path=signin_url, data=data, format="json")
            assert signin.status_code == status.HTTP_200_OK
            return signin
        else:
            raise Exception("User already exists")

    def signup_partner(self, email: str, password: str) -> HttpResponse:
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            User().create_user(email=email, password=password, role="partner")
            signin = self.signin(email=email, password=password)
            assert signin.status_code == status.HTTP_200_OK
            return signin
        else:
            raise Exception("User already exists")


class SignUpTests(APITestCase, TestUtils):
    def setUp(self) -> None:
        self.url = reverse(viewname="sign-up")
        self.SIGNUP_DATA_BAD = {"email": "test@test.test"}

    def test_successful_signup(self) -> None:
        response = self.client.post(path=self.url, data=self.USER_DATA, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(member="token", container=response.data)
        self.assertIsNotNone(response.cookies["token"])
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, self.USER_DATA["email"])

    def test_missing_fields_signup(self) -> None:
        response = self.client.post(
            path=self.url,
            data=self.SIGNUP_DATA_BAD,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESP.NOT_ENOUGH_DATA.data)

    def test_existing_email_signup(self) -> None:
        User().create_user(email="test@test.test", password="test", name="test")
        response = self.client.post(path=self.url, data=self.USER_DATA, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            RESP.ALREADY_EXISTS.data,
        )


class SignInTests(APITestCase, TestUtils):
    def setUp(self) -> None:
        self.url = reverse(viewname="sign-in")

    def test_successful_signin(self) -> None:
        self.signup_brand(
            email=self.USER_DATA["email"],
            password=self.USER_DATA["password"],
        )
        response = self.client.post(path=self.url, data=self.USER_DATA, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(member="token", container=response.data)
        self.assertIsNotNone(response.cookies["token"])
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, self.USER_DATA["email"])

    def test_missing_fields_signin(self) -> None:
        data = {"email": "test@test.com"}
        response = self.client.post(path=self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESP.NOT_ENOUGH_DATA.data)

    def test_wrong_credentials_signin(self) -> None:
        self.signup_brand(
            email=self.USER_DATA["email"],
            password=self.USER_DATA["password"],
        )
        data = {
            "email": self.USER_DATA["email"],
            "password": self.USER_DATA["password"] + "1",
        }
        response = self.client.post(path=self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, RESP.INVALID_CRED.data)


class RefreshTests(APITestCase, TestUtils):
    def setUp(self) -> None:
        self.refresh_url = reverse(viewname="refresh")
        self.sigin_url = reverse(viewname="sign-in")

    def test_successful_refresh(self) -> None:
        signup = self.signup_brand(
            email=self.USER_DATA["email"],
            password=self.USER_DATA["password"],
        )
        headers = {"Authorization": f"Bearer {signup.data["token"]}"}
        response = self.client.post(
            path=self.refresh_url,
            format="json",
            headers=headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.cookies["token"])

    def test_invalid_token_refresh(self) -> None:
        headers = {"Authorization": "Bearer BAD_TOKEN"}
        response = self.client.post(
            path=self.refresh_url,
            format="json",
            headers=headers,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_session_refresh(self) -> None:
        first_signin = self.signup_brand(
            email=self.USER_DATA["email"],
            password=self.USER_DATA["password"],
        )
        self.signin(email=self.USER_DATA["email"], password=self.USER_DATA["password"])
        headers = {"Authorization": f"Bearer {first_signin.data["token"]}"}
        response = self.client.post(
            path=self.refresh_url,
            format="json",
            headers=headers,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutTests(APITestCase, TestUtils):
    def setUp(self) -> None:
        self.url = reverse(viewname="logout")
        self.refresh_url = reverse(viewname="refresh")

    def test_successful_logout(self) -> None:
        signup = self.signup_brand(
            email=self.USER_DATA["email"],
            password=self.USER_DATA["password"],
        )
        headers = {"Authorization": f"Bearer {signup.data["token"]}"}
        response = self.client.post(path=self.url, format="json", headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(path=self.refresh_url, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_token_logout(self) -> None:
        headers = {"Authorization": "Bearer BAD_TOKEN"}
        response = self.client.post(path=self.url, format="json", headers=headers)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
