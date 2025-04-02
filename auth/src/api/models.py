from django.db import models
from django.conf import settings
from django.contrib.auth.hashers import make_password

CON = settings.CONSTANTS


class User(models.Model):
    id = models.AutoField(
        verbose_name="ID",
        primary_key=True,
    )
    name = models.CharField(
        verbose_name="Имя",
        max_length=CON.INITIALS_LEN,
    )
    password = models.CharField(
        verbose_name="Пароль",
        max_length=CON.INITIALS_LEN,
    )
    email = models.CharField(
        verbose_name="Почта",
        max_length=CON.INITIALS_LEN,
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="avatars/",
        null=True,
        blank=True,
    )
    role = models.TextField(
        verbose_name="Роль",
        choices=CON.ROLE_CHOICES,
        default="User",
        null=True,
    )
    created_at = models.DateTimeField(
        verbose_name="Дата создания",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name="Дата изменения",
        auto_now=True,
    )
    is_active = models.BooleanField(
        verbose_name="Актитивен",
        default=False,
    )

    @classmethod
    def create_user(
        self,
        email: str,
        password: str,
        name: str,
        role: str = None,
    ):
        user = self.objects.create(
            email=email,
            name=name,
            password=make_password(password=password),
            role=role,
        )
        return user

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователь"
        ordering = ("id",)


class TokenSession(models.Model):
    user = models.ForeignKey(
        verbose_name="Пользователь",
        to=User,
        on_delete=models.CASCADE,
    )
    created_date = models.DateTimeField(
        verbose_name="Дата создания",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Сессия"
        verbose_name_plural = "Сессии"
        ordering = ("created_date",)
