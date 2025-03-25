from django.conf import settings
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..utils.auth_utils import Token, auth_response_builder
from ..doc.auth_doc import (
    signup_swagger_schema,
    signin_swagger_schema,
    refresh_token_swagger_schema,
    logout_swagger_schema,
)
from ..utils.token_utils import Token
from ..utils.response_utils import response_handler
from ..models import User

RESP = settings.RESPONSES


class SignUpAPIView(APIView):
    @signup_swagger_schema()
    @response_handler
    def post(self, request) -> Response:
        name = request.data.get("name", None)
        email = request.data.get("email", None)
        password = request.data.get("password", None)

        if not email or not password or not name:
            return RESP.NOT_ENOUGH_DATA

        if User.objects.filter(email=email).exists():
            return RESP.ALREADY_EXISTS

        user = User().create_user(
            name=name,
            email=email,
            password=password,
            role="brand",
        )

        refresh = Token.for_user(user=user)
        return auth_response_builder(user=user, refresh=refresh)


class SignInAPIView(APIView):
    @signin_swagger_schema()
    @response_handler
    def post(self, request) -> Response:
        email = request.data.get("email", None)
        password = request.data.get("password", None)

        if not email or not password:
            return RESP.NOT_ENOUGH_DATA

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return RESP.NOT_FOUND

        if not check_password(password=password, encoded=user.password):
            return RESP.INVALID_CRED

        refresh = Token.for_user(user=user)

        return auth_response_builder(user=user, refresh=refresh)


class RefreshTokenAPIView(APIView):
    authentication_classes = []

    @refresh_token_swagger_schema()
    @response_handler
    def post(self, request) -> Response:
        token = request.headers.get("Authorization", None)

        if not token:
            return RESP.NOT_ENOUGH_DATA
        else:
            token = token.split(" ")[1]

        try:
            refresh = Token.refresh(token=token)
        except Exception:
            return RESP.INVALID_TOKEN

        return auth_response_builder(refresh=refresh)


class LogoutAPIView(APIView):
    authentication_classes = []

    @logout_swagger_schema()
    @response_handler
    def post(self, request) -> Response:
        token = request.headers.get("Authorization", None)

        if not token:
            return RESP.NOT_ENOUGH_DATA
        else:
            token = token.split(" ")[1]

        if Token.delete(token=token):
            return RESP.INVALID_TOKEN

        response = RESP.SUCCESS
        response.delete_cookie(key="token")
        return response


class ConfirmEmailAPIView(APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class ResetPasswordAPIView(APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class UpdatePasswordAPIView(APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK)
