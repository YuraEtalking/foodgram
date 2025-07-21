"""Модель Recipe"""
import hashlib
import time

from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.db import models

from ..constants import (
    ADMIN_ID,
    COOKING_TIME_MAX_LENGTH,
    COOKING_TIME_MIN_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
    SHORT_CODE_LENGTH
)
from .managers import RecipeManager
from .ingredient import Ingredient
from .tag import Tag


User = get_user_model()


class Recipe(models.Model):
    """Модель рецептов."""

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
        default=ADMIN_ID
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='RecipeIngredient'
    )
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=True,
        verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (мин)',
        validators=[
            MinValueValidator(COOKING_TIME_MIN_LENGTH),
            MaxValueValidator(COOKING_TIME_MAX_LENGTH)
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    shortcode = models.CharField(
        max_length=SHORT_CODE_LENGTH,
        verbose_name='Короткий код',
        blank=True,
        null=True,
    )
    objects = RecipeManager()

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.shortcode:
            code_phrase = self.name + str(time.time())
            hash_object = hashlib.md5(code_phrase.encode())
            self.shortcode = hash_object.hexdigest()[:6]
        super().save(*args, **kwargs)
