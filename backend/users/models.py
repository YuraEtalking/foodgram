from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import (
    MAX_EMAIL_LENGTH,
    MAX_USERNAME_LENGTH,
    MAX_FIRST_NAME_LENGTH,
    MAX_LAST_NAME_LENGTH
)


class User(AbstractUser):
    """Кастомная модель пользователя."""
    email = models.EmailField(max_length=MAX_EMAIL_LENGTH, unique=True,)
    username = models.CharField(max_length=MAX_USERNAME_LENGTH, unique=True,)
    first_name = models.CharField(
        'Имя',
        max_length=MAX_FIRST_NAME_LENGTH,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LAST_NAME_LENGTH,
        blank=True
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True)


class Follow(models.Model):
    """Модель подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Автор'
    )
    # Для сортировки подписок.
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки'
    )

    def __str__(self):
        return f'{self.user.username} подписан на {self.following.username}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                name='unique_user_following',
                fields=['user', 'following']
            ),
            models.CheckConstraint(
                name='s_prevent_self_follow',
                check=~models.Q(user=models.F('following'))
            ),
        ]
