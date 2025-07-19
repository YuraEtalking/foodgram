from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Recipe

class ShortLinkRedirectView(APIView):
    """Перенаправляет по короткой ссылке на рецепт."""

    def get(self, request, short_code):
        from django.http import HttpResponseRedirect
        recipe = Recipe.objects.filter(shortcode=short_code).first()
        if recipe is None:
            return Response({'error': 'Рецепт не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        recipe_id = recipe.id
        return HttpResponseRedirect(
            request.build_absolute_uri(f'/recipes/{recipe_id}')
        )
