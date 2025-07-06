from django_filters import rest_framework as filters
from .models import Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.NumberFilter(
        field_name='is_favorited',
        lookup_expr='exact'
    )
    is_in_shopping_cart = filters.NumberFilter(
        field_name='is_in_shopping_cart',
        lookup_expr='exact'
    )
    author = filters.NumberFilter(field_name='author', lookup_expr='exact')
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']
