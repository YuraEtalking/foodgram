"""Сериализаторы для приложения users"""
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from .fields import Base64ImageField


User = get_user_model()


class UserDetailSerializer(UserSerializer):
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
        return (request and request.user.is_authenticated
                and obj.subscribers.filter(user=request.user).exists())

    def get_avatar_url(self, obj):
        """Возвращает URL аватара пользователя."""
        if obj.avatar:
            return obj.avatar.url


class SubscriptionsSerializer(UserDetailSerializer):
    """Сериализатор с добавлением полей для выдачи подписок пользователя."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserDetailSerializer.Meta):
        fields = UserDetailSerializer.Meta.fields + (
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

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, attrs):
        if not attrs.get('avatar'):
            raise serializers.ValidationError(
                {'avatar': 'Аватар не может быть пустым.'}
            )
        return attrs
