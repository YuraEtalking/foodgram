"""Модуль импорта данных из csv в базу данных"""
import os
import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Импорт данных из CSV файлов'

    def handle(self, *args, **kwargs):
        self.import_ingredients()
        self.import_tags()

    def import_ingredients(self):
        """Импорт ингредиентов"""
        BASE_DIR = settings.BASE_DIR
        csv_path = os.path.join(BASE_DIR, 'data', 'ingredients.csv')
        before_count = Ingredient.objects.count()
        with open(csv_path, encoding='utf-8') as file:
            reader = csv.reader(file)
            Ingredient.objects.bulk_create(
                [
                    Ingredient(
                        name=row[0],
                        measurement_unit=row[1]
                    ) for row in reader
                ], ignore_conflicts=True
            )
            after_count = Ingredient.objects.count()
            imported_data = after_count - before_count

        self.stdout.write(
            self.style.SUCCESS(
                f'Импортированно: {imported_data} записей ингридиентов.')
        )

    def import_tags(self):
        """Импорт тегов"""
        BASE_DIR = settings.BASE_DIR
        csv_path = os.path.join(BASE_DIR, 'data', 'tags.csv')
        before_count = Ingredient.objects.count()
        with open(csv_path, encoding='utf-8') as file:
            reader = csv.reader(file)
            Tag.objects.bulk_create(
                [
                    Tag(
                        name=row[0],
                        slug=row[1]
                    ) for row in reader
                ], ignore_conflicts=True
            )
            after_count = Tag.objects.count()
            imported_data = after_count - before_count
        self.stdout.write(
            self.style.SUCCESS(
                f'Импортированно: {imported_data} записей тегов.')
        )
