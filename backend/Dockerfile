FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

RUN addgroup --system app && adduser --system --group app
RUN chown -R app:app /app
RUN chmod u+x /app/docker-start.sh

# CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000", "--reload"]
CMD ["/app/docker-start.sh"]