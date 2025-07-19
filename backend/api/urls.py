"""Модуль содержит эндпоинты для API."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.recipes import (
    IngredientViewSet,
    RecipeViewSet,
    RecipeShortLinkView,
    TagViewSet,
)
from .views.users import UserViewSet


router = DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'recipes/<int:pk>/get-link/',
        RecipeShortLinkView.as_view(),
        name='short-link'
    ),
    path('', include(router.urls)),
]
