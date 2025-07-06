"""Сериализаторы для приложения users"""
from django.conf import settings
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .fields import Base64ImageField


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Переопределяем поля и модель для регистрации новых пользователей"""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class CustomUserSerializer(UserSerializer):
    """Сериализатор для пользователей."""

    avatar = serializers.SerializerMethodField(
        'get_avatar_url',
        read_only=True,
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        """Возвращает, подписку автора на пользователя"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.subscribers.filter(user=request.user).exists()
        return False

    def get_avatar_url(self, obj):
        """Возвращает URL аватара пользователя или URL аватара по умолчанию."""
        request = self.context.get('request')
        if obj.avatar:
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        else:
            if request:
                return request.build_absolute_uri(settings.DEFAULT_AVATAR_URL)
            return settings.DEFAULT_AVATAR_URL


class SubscriptionsSerializer(CustomUserSerializer):
    """Сериализатор с добавлением полей для выдачи подписок пользователя."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        """Возвращает количество рецептов пользователя."""
        return obj.recipes.count()

    def get_recipes(self, obj):
        """Возвращает рецепты пользователя."""
        from .recipes import RecipeShortResponseSerializer
        request = self.context.get('request')
        recipes_limit = None

        if request:
            try:
                recipes_limit = int(request.query_params.get('recipes_limit'))
            except (TypeError, ValueError):
                recipes_limit = None

        recipes_queryset = obj.recipes.all()
        if recipes_limit:
            recipes_queryset = recipes_queryset[:recipes_limit]

        return RecipeShortResponseSerializer(
            recipes_queryset,
            many=True,
            context=self.context
        ).data


class AvatarUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор обновления аватара."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
