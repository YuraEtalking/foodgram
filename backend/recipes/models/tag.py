from django.db import models
from django.utils.text import slugify

from ..constants import TAG_MAX_LENGTH


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        max_length=TAG_MAX_LENGTH,
        verbose_name='Тег',
        unique=True,
    )
    slug = models.SlugField(unique=True, max_length=TAG_MAX_LENGTH,)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def clean(self):
        """Удаляем пробелы и переводим в нижний регистр."""
        if self.name:
            self.name = self.name.strip().lower()

    def save(self, *args, **kwargs):
        """Переопределяем save для автоматического вызова."""
        self.full_clean()
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
