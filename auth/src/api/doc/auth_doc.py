from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


def signup_swagger_schema():
    return swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Почта",
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Пароль",
                ),
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Имя",
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Успешная регистрация",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "userData": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="Данные пользователя",
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_STRING),
                                "email": openapi.Schema(type=openapi.TYPE_STRING),
                                "name": openapi.Schema(type=openapi.TYPE_STRING),
                                "role": openapi.Schema(type=openapi.TYPE_STRING),
                                "isActive": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                        "token": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Refresh токен"
                        ),
                    },
                ),
                headers={
                    "Set-Cookie": openapi.Parameter(
                        name="token",
                        in_=openapi.IN_HEADER,
                        type=openapi.TYPE_STRING,
                        description="Access токен",
                        required=True,
                    )
                },
            ),
            400: openapi.Response(
                description="Данные запроса некорректны",
                examples={
                    "application/json": {"error": "Недостаточно данных"},
                    "application/json": {"error": "Уже существует"},
                },
            ),
        },
        operation_description="Регистрация бренда с отправкой емейла подтверждения",
    )


def signin_swagger_schema():
    return swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="Почта"),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Пароль"
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Успешный вход",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "userData": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="Данные пользователя",
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_STRING),
                                "email": openapi.Schema(type=openapi.TYPE_STRING),
                                "name": openapi.Schema(type=openapi.TYPE_STRING),
                                "role": openapi.Schema(type=openapi.TYPE_STRING),
                                "isActive": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                        "token": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Refresh токен"
                        ),
                    },
                ),
                examples={
                    "application/json": {"token": "refresh_token"},
                },
                headers={
                    "Set-Cookie": openapi.Parameter(
                        name="token",
                        in_=openapi.IN_HEADER,
                        type=openapi.TYPE_STRING,
                        description="Access токен",
                        required=True,
                    )
                },
            ),
            400: openapi.Response(
                description="Данные запроса некорректны",
                examples={
                    "application/json": {"error": "Недостаточно данных"},
                    "application/json": {"error": "Неверные данные"},
                },
            ),
            404: openapi.Response(
                description="Ресурс не найден (ресурс с таким id/email не найден)",
                examples={
                    "application/json": {"error": "Не найдено"},
                },
            ),
        },
        operation_description="Вход в аккаунт",
    )


def refresh_token_swagger_schema():
    return swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description="Refresh токен",
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Успешное обновление токена",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "refresh": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Новый refresh токен"
                        ),
                    },
                ),
                examples={
                    "application/json": {"token": "new_refresh_token"},
                },
                headers={
                    "Set-Cookie": openapi.Parameter(
                        name="token",
                        in_=openapi.IN_HEADER,
                        type=openapi.TYPE_STRING,
                        description="Новый access токен",
                        required=True,
                    )
                },
            ),
            400: openapi.Response(
                description="Данные запроса некорректны",
                examples={
                    "application/json": {"error": "Недостаточно данных"},
                },
            ),
            401: openapi.Response(
                description="Неавторизован (недействительный или отсутствующий токен)",
                examples={
                    "application/json": {"error": "Невалидный токен"},
                },
            ),
        },
        operation_description="Обновить токены с помощью refresh токена",
    )


def logout_swagger_schema():
    return swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description="Refresh токен",
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Успешный выход из аккаунта",
                examples={
                    "application/json": {"message": "Успешно выполнено"},
                },
            ),
            400: openapi.Response(
                description="Данные запроса некорректны",
                examples={
                    "application/json": {"error": "Недостаточно данных"},
                },
            ),
            401: openapi.Response(
                description="Неавторизован (недействительный или отсутствующий токен)",
                examples={
                    "application/json": {"error": "Невалидный токен"},
                },
            ),
        },
        operation_description="Выйти из аккаунта и сбросить предыдущие токены",
    )
