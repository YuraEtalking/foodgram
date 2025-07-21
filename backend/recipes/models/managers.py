"""Модуль менеджера модели Recipe"""
from django.db import models


class RecipeQuerySet(models.QuerySet):
    """QuerySet для модели рецептов."""

    def with_user_annotations(self, user):
        """Аннотируем QuerySet избранным и списком покупок."""
        from .favorite import Favorite
        from .shopping_list import ShoppingList
        if user.is_authenticated:
            return self.annotate(
                is_favorited=models.Exists(
                    Favorite.objects.filter(
                        user=user,
                        recipe=models.OuterRef('id')
                    )
                ),
                is_in_shopping_cart=models.Exists(
                    ShoppingList.objects.filter(
                        user=user,
                        recipe=models.OuterRef('id')
                    )
                )
            )
        return self.annotate(
            is_favorited=models.Value(
                False,
                output_field=models.BooleanField()
            ),
            is_in_shopping_cart=models.Value(
                False,
                output_field=models.BooleanField()
            )
        )


class RecipeManager(models.Manager):
    """Менеджер для модели рецептов"""

    def get_queryset(self):
        """Возвращает RecipeQuerySet для модели рецептов."""
        return RecipeQuerySet(self.model, using=self._db)

    def with_user_annotations(self, user):
        """Возвращает queryset с аннотациями."""
        return self.get_queryset().with_user_annotations(user)
