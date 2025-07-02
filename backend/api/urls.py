"""Модуль содержит эндпоинты для API."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views.users import CustomUserViewSet
from .views.recipes import IngredientViewSet, RecipeViewSet, TagViewSet, RecipeShortLinkView


router = DefaultRouter()

router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'recipes/<int:pk>/get-link/',
        RecipeShortLinkView.as_view(),
        name='short-link'
    ),
    path('', include(router.urls)),
]
