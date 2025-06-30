from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import (
    EMAIL_MAX_LENGTH,
    FIRST_NAME_MAX_LENGTH,
    LAST_NAME_MAX_LENGTH,
    USERNAME_MAX_LENGTH
)
from .validators import validate_username


class User(AbstractUser):
    """Кастомная модель пользователя."""
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        verbose_name='Почта'
    )
    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        verbose_name='Никнейм',
        validators=(validate_username,)
    )
    first_name = models.CharField(
        verbose_name ='Имя',
        max_length=FIRST_NAME_MAX_LENGTH,
        blank=False
    )
    last_name = models.CharField(
        verbose_name ='Фамилия',
        max_length=LAST_NAME_MAX_LENGTH,
        blank=False
    )
    avatar = models.ImageField(
        upload_to='users/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['first_name']

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',  # Подписки пользователя
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',  # Подписчики автора
        verbose_name='Автор'
    )
    # Для сортировки подписок.
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки'
    )

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'


    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                name='unique_user_author',
                fields=['user', 'author']
            ),
            models.CheckConstraint(
                name='s_prevent_self_subscription',
                check=~models.Q(user=models.F('author'))
            ),
        ]
