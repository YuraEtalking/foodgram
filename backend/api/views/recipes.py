"""Представления для приложения рецептов в приложении api."""
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated
)
from rest_framework.response import Response

from ..serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeReadingSerializer,
    RecipeShortResponseSerializer,
    ShortLinkSerializer,
    TagSerializer
)
from ..permissions import IsAuthorOrReadOnly
from ..filters import IngredientFilter, RecipeFilter
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag
)
from ..pagination import LimitPageNumberPagination


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от действия."""
        if self.action in ['create', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeReadingSerializer

    def get_queryset(self):
        return Recipe.objects.with_user_annotations(self.request.user)

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link'
    )
    def get_short_link(self, request, pk):
        """Обрабатывает GET-запрос для получения короткой ссылки на рецепт."""
        try:
            recipe = Recipe.objects.get(pk=pk)
            domain = request.get_host()
            protocol = 'https' if request.is_secure() else 'http'
            link = f'{protocol}://{domain}/s/{recipe.shortcode}'
            serializer = ShortLinkSerializer({'short_link': link})
            return Response(serializer.data)
        except Recipe.DoesNotExist:
            return Response(
                {'error': 'Рецепт не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_list(self, request):
        """Обрабатывает GET-запрос для скачивания списка покупок."""
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__in_shopping_lists__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
            ).annotate(
                total_amount=models.Sum('amount')
            ).order_by('ingredient__name')
        )

        shopping_list_txt = 'Список покупок:\n\n'
        for ingredient in ingredients:
            shopping_list_txt += (
                f'• {ingredient["ingredient__name"]} - '
                f'{ingredient["total_amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}\n'
            )

        response = HttpResponse(
            shopping_list_txt,
            content_type='text/plain; charset=utf-8'
        )
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_list.txt"'

        return response

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='(?P<action_type>shopping_cart|favorite)'
    )
    def manage_shopping_list_and_favorite_recipe(
            self,
            request,
            pk=None,
            action_type=None
    ):
        """Обрабатывает запросы для списка покупок и избранными рецептами."""
        recipe = self.get_object()
        user = request.user
        serializer_class = RecipeShortResponseSerializer

        if action_type == 'shopping_cart':
            model_class = ShoppingList
            message = 'списке покупок'
        elif action_type == 'favorite':
            model_class = Favorite
            message = 'избранном'
        else:
            return Response({'error': 'Неверный запрос'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            obj, created = model_class.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            if created:
                serializer = serializer_class(
                    recipe,
                    context={'request': request}
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'error': f'Рецепт уже в {message}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == 'DELETE':
            obj = get_object_or_404(
                model_class,
                user=request.user,
                recipe=recipe
            )
            deleted_count, _ = obj.delete()
            if deleted_count:
                return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ModelViewSet):
    """Представление для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    http_method_names = ['get']


class TagViewSet(viewsets.ModelViewSet):
    """Представление для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
