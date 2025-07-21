from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from ..constants import (AMOUNT_MAX_LENGTH, AMOUNT_MIN_LENGTH)
from .recipe import Recipe
from .ingredient import Ingredient


class RecipeIngredient(models.Model):
    """Модель, для связи между рецептом и ингредиентом с указанием кол-ва."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(AMOUNT_MIN_LENGTH),
            MaxValueValidator(AMOUNT_MAX_LENGTH)
        ]
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                name='unique_recipe_ingredient',
                fields=['recipe', 'ingredient']
            ),
        ]
