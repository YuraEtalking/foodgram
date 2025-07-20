"""Модуль для админки приложения рецептов."""
from django.contrib import admin
from django.db.models import Count

# from .constants import SHORT_TEXT_IN_ADMIN_LENGTH
from .models import (
    Ingredient,
    Favorite,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag
)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка для модели Favorite."""

    list_display = (
        'user',
        'recipe',
        'created_at'
    )
    search_fields = ['user__username', 'recipe__name']


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Админка для модели ShoppingList."""

    list_display = (
        'user',
        'recipe',
        'created_at'
    )
    search_fields = ['user__username', 'recipe__name']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для модели Ingredient."""

    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ['name__icontains']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для модели Tag."""

    list_display = (
        'name',
        'slug',
    )
    search_fields = ['name__icontains']
    prepopulated_fields = {'slug': ('name',)}


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн для ингредиентов в рецепте."""

    model = RecipeIngredient
    extra = 1
    min_num = 1
    fields = ['ingredient', 'amount']


# Скрыл некоторые поля, что бы не перегружать таблицу в админке.
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для модели Recipe."""

    list_display = (
        'name',
        'author',
        # 'cooking_time',
        # 'display_text',
        'image',
        # 'display_ingredients',
        # 'display_tags',
        'favorites_count',
        'created_at',
        'updated_at',
    )
    search_fields = ['name', 'author__username']
    list_filter = ['tags']
    inlines = [RecipeIngredientInline]
    exclude = ['ingredients']

    def get_queryset(self, request):
        """Возвращает queryset с аннотацией favorites_count."""
        return super().get_queryset(request).prefetch_related(
            'recipeingredient_set__ingredient',
            'tags'
        ).annotate(favorites_count=Count('favorited_by'))

    # @admin.display(description='Ингредиенты')
    # def display_ingredients(self, obj):
    #     """Возвращает строку с ингредиентами и количеством для рецепта."""
    #     recipe_ingredients = obj.recipeingredient_set.all()
    #     return ', '.join(
    #         f'{r_i.ingredient.name} '
    #         f'({r_i.amount} {r_i.ingredient.measurement_unit})'
    #         for r_i in recipe_ingredients
    #     )

    # @admin.display(description='Теги')
    # def display_tags(self, obj):
    #     """Возвращает строку с тегами рецепта."""
    #     return ', '.join(
    #         tag.name for tag in obj.tags.all())

    @admin.display(description='В избранном', ordering='favorites_count')
    def favorites_count(self, obj):
        """Возвращает количество добавлений в избранное."""
        return obj.favorites_count

    # @admin.display(description='Описание')
    # def display_text(self, obj):
    #     """Усекает текст описания"""
    #     return ((obj.text[:SHORT_TEXT_IN_ADMIN_LENGTH] + '...')
    #             if len(obj.text) > SHORT_TEXT_IN_ADMIN_LENGTH else obj.text)
