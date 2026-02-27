FROM python:3.13-slim AS build

WORKDIR /app

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "sleep 1 && python manage.py migrate && gunicorn --bind 0.0.0.0:8000 Detective_API.wsgi:application"]