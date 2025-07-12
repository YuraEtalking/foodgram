"""Модуль импорта данных из csv в базу данных"""
import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Импорт данных из CSV файлов'

    def handle(self, *args, **kwargs):
        self.import_ingredients()
        self.import_tags()

    def import_ingredients(self):
        """Импорт ингредиентов"""
        csv_path = '/app/data/ingredients.csv'

        with open(csv_path, encoding='utf-8') as file:
            reader = csv.reader(file)
            imported_data = 0
            for row in reader:
                Ingredient.objects.create(
                    name=row[0],
                    measurement_unit=row[1],
                )
                imported_data += 1
        self.stdout.write(
            self.style.SUCCESS(
                f'Импортированно: {imported_data} записей ингридиентов.')
        )

    def import_tags(self):
        """Импорт ингредиентов"""
        csv_path = '/app/data/tags.csv'

        with open(csv_path, encoding='utf-8') as file:
            reader = csv.reader(file)
            imported_data = 0
            for row in reader:
                Tag.objects.create(
                    name=row[0],
                    slug=row[1],
                )
                imported_data += 1
        self.stdout.write(
            self.style.SUCCESS(
                f'Импортированно: {imported_data} записей тегов.')
        )
