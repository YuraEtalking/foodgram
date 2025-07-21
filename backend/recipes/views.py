"""Представления для приложения рецептов."""
from django.http import HttpResponseRedirect
from rest_framework.views import APIView

from .models import Recipe


class ShortLinkRedirectView(APIView):
    """Перенаправляет по короткой ссылке на рецепт."""

    def get(self, request, short_code):
        recipe = Recipe.objects.filter(shortcode=short_code).first()
        if recipe is None:
            return HttpResponseRedirect(
                request.build_absolute_uri('/not-found'))
        recipe_id = recipe.id
        return HttpResponseRedirect(
            request.build_absolute_uri(f'/recipes/{recipe_id}')
        )
