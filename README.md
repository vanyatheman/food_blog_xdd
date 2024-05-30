# food_blog_xdd
Фуд блог с рецептами и подпиской, избранными блюдами и списком для покупок

### Запуск проекта на локальной машине:

- Клонировать репозиторий:
```
https://github.com/vanyatheman/food_blog_xdd.git
```

- В директории infra создать файл .env и заполнить своими данными по аналогии с example.env:
```
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5434
SECRET_KEY='секретный ключ Django'
```

- Создать и запустить контейнеры Docker
```
docker compose up -d
```

После успешной сборки выполнить миграции:
```
docker compose exec backend python manage.py migrate
```

- Создать суперпользователя:
```
docker compose exec backend python manage.py createsuperuser
```

- Собрать статику:
```
docker compose exec backend python manage.py collectstatic --noinput
```

- Наполнить базу данных содержимым из файла backend/data/ingredients.json:
```
docker compose exec backend python manage.py import_csv
```

- Для остановки контейнеров Docker:
```
docker compose down -v      # с их удалением
docker compose stop         # без удаления
```

- После запуска проект будут доступен по адресу: [http://localhost/](http://localhost/)

