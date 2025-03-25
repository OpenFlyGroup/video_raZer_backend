from rest_framework_simplejwt.tokens import RefreshToken

from ..models import TokenSession, User


def is_session_valid(user_id, created_date) -> TokenSession | None:
    try:
        TokenSession.objects.get(user_id=user_id, created_date=created_date)
        return True
    except TokenSession.DoesNotExist:
        return False


def delete_session(user_id) -> int:
    try:
        user = User.objects.get(id=user_id)
        TokenSession.objects.get(user=user).delete()
        return 0
    except TokenSession.DoesNotExist:
        return -1


def create_session(user) -> TokenSession:
    if TokenSession.objects.filter(user=user).exists():
        TokenSession.objects.filter(user=user).delete()
    session = TokenSession.objects.create(user=user)
    return session


class Token(RefreshToken):
    @classmethod
    def for_user(cls, user) -> RefreshToken:
        token = super().for_user(user=user)
        session = create_session(user=user)
        token["user_id"] = user.id
        token["created"] = session.created_date.isoformat()
        return token

    @classmethod
    def refresh(cls, token) -> RefreshToken:
        token = RefreshToken(token=token)
        if not is_session_valid(
            user_id=token["user_id"],
            created_date=token["created"],
        ):
            raise Exception("Session expired")
        user = User.objects.get(id=token["user_id"])
        session = create_session(user=user)
        token["created"] = session.created_date.isoformat()
        return token

    @classmethod
    def delete(cls, token) -> int:
        try:
            token = RefreshToken(token=token)
            if not is_session_valid(
                user_id=token["user_id"],
                created_date=token["created"],
            ):
                return -1
            user = User.objects.get(id=token["user_id"])
        except Exception:
            return -1
        return delete_session(user_id=user.id)
