"""Модель Favorite"""
from django.contrib.auth import get_user_model
from django.db import models

from .user_recipe_base import UserRecipeBase
from .recipe import Recipe


User = get_user_model()


class Favorite(UserRecipeBase):
    """Модель избранного."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                name='unique_user_recipe_favorite',
                fields=['user', 'recipe']
            ),
        ]

    def __str__(self):
        return f'{self.recipe.name} в избранном у {self.user.username}.'
