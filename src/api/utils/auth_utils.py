from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..models import User
from ..utils.token_utils import Token, is_session_valid
from ..utils.user_utils import user_info


class JWTAuth(JWTAuthentication):
    def authenticate(self, request) -> tuple[User, Token]:
        cookie_token = request.COOKIES.get("token")
        if cookie_token is None:
            raise AuthenticationFailed(detail="No token provided", code="invalid_token")
        try:
            validated_token = self.get_validated_token(raw_token=cookie_token)
        except AuthenticationFailed:
            raise AuthenticationFailed(
                detail="Invalid token", code="invalid_token"
            ) from None
        return self.get_user(validated_token=validated_token), validated_token

    def get_user(self, validated_token) -> User:
        try:
            user_id = validated_token.get(key="user_id")
            created = validated_token.get(key="created")
            user = User().get_by_id(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed(
                detail="User not found", code="user_not_found"
            ) from None
        if not is_session_valid(user_id=user, created_date=created):
            raise AuthenticationFailed(detail="Session expired", code="session_expired")
        return user


def auth_response_builder(user: User = None, refresh: Token = None) -> dict:
    response_data = {}
    if user:
        response_data["userData"] = user_info(user=user)
    if refresh:
        response_data["token"] = str(refresh)
    response = Response(data=response_data, status=status.HTTP_200_OK)
    if refresh:
        response.set_cookie(
            key="token",
            value=str(refresh.access_token),
            max_age=2592000,
            # httponly=True,
            # secure=True,
            # samesite="Lax",
            # domain="localhost",
        )
    return response


def activate_user(uidb64, token) -> int:
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(id=int(uid))
        print(user)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return -1

    if default_token_generator.check_token(user, token):
        user.active = True
        user.save()
        return 1
    else:
        return -1


def reset_password(uidb64, token, password) -> int:
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(id=int(uid))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return -1

    if default_token_generator.check_token(user, token):
        user.set_password(password=password)
        user.save()
        return 1
    else:
        return -1


def update_password(user: User, old_password: str, new_password: str) -> int:
    if check_password(password=old_password, encoded=user.password):
        user.set_password(password=new_password)
        user.save()
        return 1
    else:
        return -1
