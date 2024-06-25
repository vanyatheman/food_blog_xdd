Food Blog with Recipes, Subscription, Favorite Dishes, and Shopping List
Project Launch on Local Machine:
Clone the Repository:

```bash
git clone https://github.com/vanyatheman/food_blog_xdd.git
```
Create a .env File in the infra Directory:
Fill it with your own data based on the example provided in example.env:

```bash
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5434
SECRET_KEY='your Django secret key'
```
Create and Start Docker Containers:

```bash
docker compose up -d
```
After Successful Build, Apply Migrations:

```bash
docker compose exec backend python manage.py migrate
```
Create a Superuser:

```bash
docker compose exec backend python manage.py createsuperuser
```
Collect Static Files:

```bash
docker compose exec backend python manage.py collectstatic --noinput
```
Populate the Database with Content from backend/data/ingredients.json:

```bash
docker compose exec backend python manage.py import_csv
```
To Stop Docker Containers:

```bash
docker compose down -v      # with deletion
docker compose stop         # without deletion
```
After launching, the project will be available at: http://localhost/
