from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint

from api.validators import validate_username


class User(AbstractUser):
    """
    Модель пользователя.

    Поля:
    - email: почта пользователя
    - username: имя пользователя
    - first_name: имя пользователя
    - last_name: фамилия пользователя
    - password: пароль пользователя
    """
    email = models.EmailField(
        verbose_name='Почта',
        max_length=254,
        unique=True
    )

    username = models.CharField(
        verbose_name='Имя пользователя',
        validators=(validate_username,),
        max_length=150
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150
    )

    password = models.CharField(
        verbose_name='Пароль',
        max_length=150
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('pk',)
        constraints = (
            models.UniqueConstraint(
                fields=('email', 'username'),
                name='unique_auth'),
        )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='following',
        null=False
    )

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='followers',
        null=False
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ('-pk',)
        constraints = (
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription'),
        )

    def __str__(self):
        return str(self.user)
