from .base import *
import os
import dj_database_url

SECRET_KEY = 'django-insecure-metti-qui-una-stringa-qualsiasi'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

database_url = os.environ.get('DATABASE_URL')
if database_url:
    DATABASES = {'default': dj_database_url.config(default=database_url)}
else:
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}