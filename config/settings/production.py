from .base import *
import os
import dj_database_url

SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
CSRF_TRUSTED_ORIGINS = [f'https://{host}' for host in ALLOWED_HOSTS if host]
DATABASES = {'default': dj_database_url.config(conn_max_age=600, conn_health_checks=True)}