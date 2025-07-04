# from django.contrib.admin import action
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag
)
from api.serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeReadingSerializer,
    RecipeShortResponseSerializer,
    ShortLinkSerializer,
    TagSerializer
)
from yaml import serialize


class RecipeShortLinkView(APIView):
    def get(self, request, pk):
        try:
            recipe = Recipe.objects.get(pk=pk)
            serializer = ShortLinkSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data)
        except Recipe.DoesNotExist:
            return Response(
                {'error': 'Рецепт не найден'},
                status=status.HTTP_404_NOT_FOUND
            )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeReadingSerializer

    @action(
        detail=False,
        methods=['get'],
        # permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_list(self, request):
        shopping_list_recipe = ShoppingList.objects.filter(
            user=request.user
        ).values_list('recipe_id', flat=True)

        ingredients = RecipeIngredient.objects.filter(
            recipe_id__in=shopping_list_recipe
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

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
        url_path='shopping_cart'
    )
    def add_recipe_in_shopping_list(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            shoppinglist, created = ShoppingList.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )
            if created:
                serializer = RecipeShortResponseSerializer(
                    recipe,
                    context={'request': request}
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'error': 'Уже в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == 'DELETE':
            shoppinglist = get_object_or_404(
                ShoppingList,
                user=request.user,
                recipe=recipe
            )

            if shoppinglist:
                shoppinglist.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'error': 'рецепта нет в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )



class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get',]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get',]
