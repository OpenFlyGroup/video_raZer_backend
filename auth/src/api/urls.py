from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from .views.auth_views import *

schema_view = get_schema_view(
    info=openapi.Info(
        title="VideoRazer backend API",
        default_version="v1",
        description="VideoRazer backend",
        terms_of_service="https://www.org.com",
        contact=openapi.Contact(email="org@gmail.com"),
        license=openapi.License(name="Org License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # ? Документация
    path(
        route="swagger/",
        view=schema_view.with_ui(renderer="swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    #######################################################################################
    # ? Аутентификация
    path(
        route="auth/signup",
        view=SignUpAPIView.as_view(),
        name="sign-up",
    ),
    path(
        route="auth/signin",
        view=SignInAPIView.as_view(),
        name="sign-in",
    ),
    path(
        route="auth/logout",
        view=LogoutAPIView.as_view(),
        name="logout",
    ),
    path(
        route="auth/refresh",
        view=RefreshTokenAPIView.as_view(),
        name="refresh",
    ),
    path(
        route="auth/confirm-email/<uidb64>/<token>",
        view=ConfirmEmailAPIView.as_view(),
        name="confirm-email",
    ),
    path(
        route="auth/reset-password",
        view=ResetPasswordAPIView.as_view(),
        name="reset-password",
    ),
    path(
        route="auth/update-password",
        view=UpdatePasswordAPIView.as_view(),
        name="update-password",
    ),
]
