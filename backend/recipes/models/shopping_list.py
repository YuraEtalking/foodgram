from django.contrib.auth import get_user_model
from django.db import models

from .recipe import Recipe
from .user_recipe_base import UserRecipeBase


User = get_user_model()


class ShoppingList(UserRecipeBase):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_lists',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_lists',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                name='unique_user_recipe_shopping_list',
                fields=['user', 'recipe']
            ),
        ]

    def __str__(self):
        return f'{self.recipe.name} в списке покупок у {self.user.username}.'
