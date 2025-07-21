"""Модель Ingredient"""
from django.db import models

from ..constants import (INGREDIENT_MAX_LENGTH, MEASUREMENT_UNIT_MAX_LENGTH)


class Ingredient(models.Model):
    """Модель ингридиентов."""

    name = models.CharField(
        max_length=INGREDIENT_MAX_LENGTH,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                name='unique_name_measurement_unit',
                fields=['name', 'measurement_unit']
            ),
        ]

    def __str__(self):
        return self.name
