"""Модуль менеджера модели Recipe"""
from django.db import models


class RecipeQuerySet(models.QuerySet):
    def with_user_annotations(self, user):
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
    def get_queryset(self):
        return RecipeQuerySet(self.model, using=self._db)

    def with_user_annotations(self, user):
        return self.get_queryset().with_user_annotations(user)
