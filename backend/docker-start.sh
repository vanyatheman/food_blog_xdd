#!/usr/bin/env bash

set -ex

python manage.py migrate

python manage.py collectstatic --noinput

python manage.py import_csv

gunicorn backend.wsgi:application --bind 0:8000 --reload
