"""Модуль импорта данных из csv в базу данных"""
import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из CSV файлов'

    def handle(self, *args, **kwargs):
        self.import_ingredients()

    def import_ingredients(self):
        """Импорт ингредиентов"""
        BASE_DIR = settings.BASE_DIR
        csv_path = os.path.join(BASE_DIR, '..', 'data', 'ingredients.csv')

        with open(csv_path, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            imported_data = 0
            for row in reader:
                columns = list(row.keys())
                Ingredient.objects.create(
                    name=row[columns[0]],
                    measurement_unit=row[columns[1]],
                )
                imported_data += 1
        self.stdout.write(
            self.style.SUCCESS(
                f'Импортированно: {imported_data} записей.')
        )
