import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient

# from users.models import User

DICT = {
    Ingredient: 'ingredients.csv',
}


class Command(BaseCommand):
    help = 'Импортирует данные из csv в базу данных'

    def handle(self, *args, **options):
        for model, base in DICT.items():
            with open(  f'data/{base}', 'r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)

                objs_to_create = []
                for data in reader:
                    obj = model(**data)
                    objs_to_create.append(obj)
                model.objects.bulk_create(objs_to_create)
            self.stdout.write(self.style.SUCCESS(
                f'{base} imported successfully'
            ))
