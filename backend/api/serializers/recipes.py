"""Сериализаторы для приложения рецептов."""
import hashlib

from rest_framework import serializers

from .fields import Base64ImageField
from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
    ShortCodeRecipe
)
from .users import CustomUserSerializer


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

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadingSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""

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

    ingredients = RecipeIngredientSerializer(many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
        # allow_empty=False
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

                all_id = [i['id'] for i in value[field]]
                if len(set(all_id)) != len(all_id):
                    raise serializers.ValidationError(
                        {field: f'В поле '
                                f'"{field}" элементы не могут повторяться.'})

        return value


    def create(self, validated_data):
        """Переопределяем create для обработки связанных данных."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        return recipe

    def update(self, recipe, validated_data):
        """Переопределяем update для обработки обновления связанных данных."""
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(recipe, attr, value)
        recipe.save()

        if tags is not None:
            recipe.tags.set(tags)

        if ingredients is not None:
            recipe.recipeingredient_set.all().delete()

            for ingredient in ingredients:
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient['id'],
                    amount=ingredient['amount']
                )
        return recipe

    def to_representation(self, recipe):
        """Указываем какой сериализатор должен формировать ответ."""
        return RecipeReadingSerializer(recipe, context=self.context).data


class ShortLinkSerializer(serializers.Serializer):
    """Сериализатор для формирования короткой ссылки на рецепт."""

    short_link = serializers.SerializerMethodField(source='*')

    def get_short_link(self, obj):
        """Формирует короткую ссылку."""
        short_code = self.get_or_create_short_code(obj)
        request = self.context.get('request')
        domain = request.get_host()
        protocol = 'https' if request.is_secure() else 'http'
        return f'{protocol}://{domain}/s/{short_code}'

    def get_or_create_short_code(self, recipe):
        """Получает существующий или создает новый короткий код."""
        existing_code = ShortCodeRecipe.objects.filter(recipe=recipe).first()
        if existing_code:
            return existing_code.shortcode

        return self.generate_short_code(recipe)

    def generate_short_code(self, recipe):
        """Используем часть хеша MD5."""
        hash_object = hashlib.md5(str(recipe.id).encode())
        short_code = hash_object.hexdigest()[:6]
        ShortCodeRecipe.objects.create(
            recipe=recipe,
            shortcode=short_code
        )
        return short_code

    def to_representation(self, instance):
        """Меняем short_link на short-link, для соответствия redoc"""
        data = super().to_representation(instance)
        return {'short-link': data['short_link']}


class RecipeShortResponseSerializer(serializers.ModelSerializer):
    """Формирует ответ при добавлении в избранное или список покупок"""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
