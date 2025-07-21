from django.db import models


class UserRecipeBase(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']
