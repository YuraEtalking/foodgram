from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from recipes.models import Ingredient, Recipe, Tag
from api.serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeReadingSerializer,
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


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get',]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get',]
