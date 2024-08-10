from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from rest_framework.authtoken.models import Token

from apps.users.validators import email_validator, username_validator


class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, **extra_fields)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Имя пользователя",
        unique=True,
        error_messages={
            "unique": "Пользователь с таким именем уже существует.",
        },
    )

    is_staff = models.BooleanField(
        "статус персонала",
        default=False,
        help_text="Отметьте, если пользователь может входить в административную часть сайта.",
    )

    is_active = models.BooleanField(
        "активный",
        default=True,
        help_text="Отметьте, если пользователь должен считаться активным. "
        "Уберите эту отметку вместо удаления учётной записи.",
    )

    email = models.EmailField(unique=True, validators=(email_validator,), verbose_name="Электронная почта")
    date_joined = models.DateTimeField("дата регистрации", default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ("email",)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return "admin" if self.is_staff or self.is_superuser else self.username

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class ProxyGroup(Group):
    """Ordinary django's Group. The class is required to register model in `users` app."""

    class Meta:
        proxy = True
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class ProxyToken(Token):
    """
    Proxy mapping pk to user pk for use in admin.
    """

    @property
    def pk(self):
        return self.user_id

    class Meta:
        proxy = True
        verbose_name = "Токен"
        verbose_name_plural = "Токены"
