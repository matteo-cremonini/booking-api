#!/bin/sh

echo 'Waiting for PostgreSQL to be ready...'

while ! nc -z db 5432; do
  sleep 0.1
done

echo 'PostgreSQL is ready!'

echo 'Running collectstatic...'
python manage.py collectstatic --noinput

echo 'Running migrations...'
python manage.py migrate

echo 'Starting server...'
exec "$@"
