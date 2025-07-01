"""Модуль содержит эндпоинты для API."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views.users import CustomUserViewSet
from .views.recipes import IngredientViewSet, RecipeViewSet, TagViewSet


router = DefaultRouter()

router.register(r'users', CustomUserViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]