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
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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

    def check_user_relation(self, obj, relation_name):
        """Существует ли запись в отношении relation_name для пользователя."""
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and getattr(
                    obj,
                    relation_name
                ).filter(user=request.user).exists())

    def get_is_favorited(self, obj):
        """Проверяем находится ли рецепт в избранном."""
        return self.check_user_relation(obj, 'favorited_by')

    def get_is_in_shopping_cart(self, obj):
        """Проверяем находится ли рецепт в списке покупок."""
        return self.check_user_relation(obj, 'in_shopping_lists')


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
            if field in value:
                if not value[field]:
                    raise serializers.ValidationError(
                        {field: f'В поле '
                                f'"{field}" список не может быть пустым.'})

                if field == 'ingredients':
                    print(f'{value[field]}')
                    all_id = [i['ingredient'].id for i in value[field]]
                else:
                    all_id = [i.id for i in value[field]]
                if len(set(all_id)) != len(all_id):
                    raise serializers.ValidationError(
                        {field: f'В поле '
                                f'"{field}" элементы не могут повторяться.'})

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

    def create(self, validated_data):
        """Переопределяем create для обработки связанных данных."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        with transaction.atomic():
            validated_data['author'] = self.context['request'].user
            recipe = Recipe.objects.create(**validated_data)
            recipe.tags.set(tags)

            self.add_ingredients_to_recipe(ingredients, recipe)

        return recipe

    def update(self, recipe, validated_data):
        """Переопределяем update для обработки обновления связанных данных."""
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        with transaction.atomic():
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

    short_link = serializers.SerializerMethodField()

    def get_short_link(self, obj):
        """Формирует короткую ссылку."""
        if not obj.shortcode:
            obj.save()
        request = self.context.get('request')
        domain = request.get_host()
        protocol = 'https' if request.is_secure() else 'http'
        return f'{protocol}://{domain}/s/{obj.shortcode}'


    def to_representation(self, instance):
        """Меняем short_link на short-link, для соответствия redoc"""
        data = super().to_representation(instance)
        return {'short-link': data['short_link']}


class RecipeShortResponseSerializer(serializers.ModelSerializer):
    """Формирует ответ при добавлении в избранное или список покупок"""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
