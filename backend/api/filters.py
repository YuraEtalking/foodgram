"""Модуль фильтров."""
from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    """Фильтр для модели Ingredient по названию ингредиента."""

    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(filters.FilterSet):
    """Фильтр для модели Recipe."""

    is_favorited = filters.BooleanFilter(field_name='is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart'
    )
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']
