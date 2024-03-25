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
            with open(
                f'D:/Dev/foodgram-project-react/data/{base}',
                'r',
                encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file)

                objs_to_create = []
                for data in reader:
                    # if model.objects.filter(id=data['id']).exists():
                    #     raise Exception(
                    #         'БД не пустая, удалите БД и сделайте миграции.'
                    #     )
                    obj = model(**data)
                    objs_to_create.append(obj)
                model.objects.bulk_create(objs_to_create)
            self.stdout.write(self.style.SUCCESS(
                f'{base} imported successfully'
            ))
