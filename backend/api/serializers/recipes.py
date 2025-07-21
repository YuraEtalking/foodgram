"""Сериализаторы для приложения рецептов."""
from django.db import transaction
from rest_framework import serializers

from .fields import Base64ImageField
from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag
)
from .users import UserDetailSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингридиентов"""

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тегов"""

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели RecipeIngredient"""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
        write_only=True
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    ingredient_id = serializers.ReadOnlyField(
        source='ingredient.id',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'ingredient_id', 'name', 'measurement_unit', 'amount')

    def to_representation(self, instance):
        """Переопределяем вывод, чтобы id был id ингредиента"""
        rep = super().to_representation(instance)
        rep['id'] = rep.pop('ingredient_id')
        return rep


class RecipeReadingSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""

    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
        source='recipeingredient_set'
    )
    tags = TagSerializer(many=True, read_only=True)
    author = UserDetailSerializer(read_only=True)
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True,
        default=False
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'image',
            'name',
            'text',
            'cooking_time',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        extra_kwargs = {
            'name': {'required': True, 'allow_blank': False},
            'text': {'required': True, 'allow_blank': False},
            'cooking_time': {'required': True},
        }

    def validate(self, value):
        """Валидация уникальности и наличия данных в ingredients и tags"""
        for field in ('ingredients', 'tags'):
            if field not in value:
                raise serializers.ValidationError(
                    {field: f'Поле "{field}" отсутствует.'}
                )

            if not value[field]:
                raise serializers.ValidationError(
                    {field: f'В поле '
                            f'"{field}" список не может быть пустым.'}
                )

            if field == 'ingredients':
                all_id = [i['ingredient'].id for i in value[field]]
            else:
                all_id = [i.id for i in value[field]]
            if len(set(all_id)) != len(all_id):
                raise serializers.ValidationError(
                    {field: f'В поле '
                            f'"{field}" элементы не могут повторяться.'}
                )

        return value

    def add_ingredients_to_recipe(self, ingredients, recipe):
        """Вспомогательная функция для методов create и update"""
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])

    @transaction.atomic
    def create(self, validated_data):
        """Переопределяем create для обработки связанных данных."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        self.add_ingredients_to_recipe(ingredients, recipe)

        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        """Переопределяем update для обработки обновления связанных данных."""
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        recipe = super().update(recipe, validated_data)
        recipe.tags.set(tags)
        recipe.ingredients.clear()

        self.add_ingredients_to_recipe(ingredients, recipe)

        return recipe

    def to_representation(self, recipe):
        """Указываем какой сериализатор должен формировать ответ."""
        return RecipeReadingSerializer(recipe, context=self.context).data


class ShortLinkSerializer(serializers.Serializer):
    """Сериализатор для формирования короткой ссылки на рецепт."""

    short_link = serializers.CharField()

    def to_representation(self, instance):
        """Меняем short_link на short-link, для соответствия redoc"""
        data = super().to_representation(instance)
        return {'short-link': data['short_link']}


class RecipeShortResponseSerializer(serializers.ModelSerializer):
    """Формирует ответ при добавлении в избранное или список покупок"""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
