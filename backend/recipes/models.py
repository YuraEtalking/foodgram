"""Модуль моделей для приложения рецептов."""
import hashlib

from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

from .constants import (
    ADMIN_ID,
    AMOUNT_MAX_LENGTH,
    AMOUNT_MIN_LENGTH,
    COOKING_TIME_MAX_LENGTH,
    COOKING_TIME_MIN_LENGTH,
    INGREDIENT_MAX_LENGTH,
    MEASUREMENT_UNIT_MAX_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
    TAG_MAX_LENGTH,
    SHORT_CODE_LENGTH
)


User = get_user_model()


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        max_length=TAG_MAX_LENGTH,
        verbose_name='Тег',
        unique=True,
    )
    slug = models.SlugField(unique=True, max_length=TAG_MAX_LENGTH,)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def clean(self):
        """Удаляем пробелы и переводим в нижний регистр."""
        if self.name:
            self.name = self.name.strip().lower()

    def save(self, *args, **kwargs):
        """Переопределяем save для автоматического вызова."""
        self.full_clean()
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


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

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.shortcode:
            super().save(*args, **kwargs)
            hash_object = hashlib.md5(str(self.id).encode())
            self.shortcode = hash_object.hexdigest()[:6]
            Recipe.objects.filter(pk=self.pk).update(shortcode=self.shortcode)
        else:
            super().save(*args, **kwargs)


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


class UserRecipeBase(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


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
