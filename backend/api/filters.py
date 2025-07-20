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

    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует рецепты, в избранном у текущего пользователя."""
        user = getattr(self.request, 'user', None)
        if value and user and user.is_authenticated:
            return queryset.filter(favorited_by__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты, в списке покупок у текущего пользователя."""
        user = getattr(self.request, 'user', None)
        if value and user and user.is_authenticated:
            return queryset.filter(in_shopping_lists__user=user)
        return queryset
