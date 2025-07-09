from django.contrib import admin
from django.db.models import Count

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
    list_display = (
        'user',
        'recipe',
        'created_at'
    )
    search_fields = ['user__username', 'recipe__name']


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
        'created_at'
    )
    search_fields = ['user__username', 'recipe__name']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ['name__icontains']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ['name__icontains']
    prepopulated_fields = {'slug': ('name',)}


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1
    fields = ['ingredient', 'amount']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'display_shortcode',
        'author',
        'cooking_time',
        'text',
        'image',
        'display_ingredients',
        'display_tags',
        'favorites_count',
        'created_at',
        'updated_at',
    )
    search_fields = ['name', 'author__username']
    list_filter = ['tags']
    inlines = [RecipeIngredientInline]
    exclude = ['ingredients']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'recipeingredient_set__ingredient',
            'tags'
        ).annotate(favorites_count=Count('favorited_by'))

    @admin.display(description='Ингредиенты')
    def display_ingredients(self, obj):
        recipe_ingredients = obj.recipeingredient_set.all()
        return ', '.join(
            f'{r_i.ingredient.name} '
            f'({r_i.amount} {r_i.ingredient.measurement_unit})'
            for r_i in recipe_ingredients
        )

    @admin.display(description='Теги')
    def display_tags(self, obj):
        return ', '.join(
            tag.name for tag in obj.tags.all())

    @admin.display(description='В избранном', ordering='favorites_count')
    def favorites_count(self, obj):
        return obj.favorites_count

    def display_shortcode(self, obj):
        shortcode_obj = obj.shortcode.first()
        return shortcode_obj.shortcode if shortcode_obj else 'Нет кода'
    display_shortcode.short_description = 'Короткий код'
