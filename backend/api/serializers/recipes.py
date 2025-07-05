"""Сериализаторы для приложения рецептов."""
import hashlib

from rest_framework import serializers

from recipes.models import (
    Ingredient,
    Favorite,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag
)
from .users import Base64ImageField, CustomUserSerializer


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
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadingSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe с вложенными и дополнительными полями."""
    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
        source='recipeingredient_set'
    )
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
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
        """Cуществует ли запись в отношении relation_name для пользователя."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return getattr(
                obj,
                relation_name
            ).filter(user=request.user).exists()
        return False

    def get_is_favorited(self, obj):
        """Проверяем находится ли рецепт в избранном."""
        return self.check_user_relation(obj, 'favorited_by')

    def get_is_in_shopping_cart(self, obj):
        """Проверяем находится ли рецепт в списке покупок."""
        return self.check_user_relation(obj, 'in_shopping_lists')


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True,
        allow_empty=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
        allow_empty=False
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

    def validate_ingredients(self, value):
        """Дополнительная валидация для ingredients"""
        if not value:
            raise serializers.ValidationError(
                'Список ингредиентов не может быть пустым')

        for ingredient in value:
            if 'id' not in ingredient or 'amount' not in ingredient:
                raise serializers.ValidationError(
                    'Каждый ингредиент должен содержать "id" и "amount"'
                )
            if not isinstance(ingredient['amount'], (int, float)) or \
                    ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть положительным числом'
                )
        return value

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags is not None:
            instance.tags.set(tags)

        if ingredients is not None:
            instance.recipeingredient_set.all().delete()

            for ingredient in ingredients:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient_id=ingredient['id'],
                    amount=ingredient['amount']
                )
        return instance

    def to_representation(self, instance):
        return RecipeReadingSerializer(instance, context=self.context).data


class ShortLinkSerializer(serializers.Serializer):
    short_link = serializers.SerializerMethodField(source='*')

    def get_short_link(self, obj):
        short_code = self.generate_short_code(obj.id)
        request = self.context.get('request')
        domain = request.get_host()
        protocol = 'https' if request.is_secure() else 'http'
        return f'{protocol}://{domain}/s/{short_code}'

    def generate_short_code(self, recipe_id):
        hash_object = hashlib.md5(str(recipe_id).encode())
        return hash_object.hexdigest()[:3]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {'short-link': data['short_link']}


class RecipeShortResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
