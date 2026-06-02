from .base import *
import os
import dj_database_url

SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False

_railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
_allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = (
    [h.strip() for h in _allowed_hosts_env.split(',') if h.strip()]
    or ([_railway_domain] if _railway_domain else [])
)
CSRF_TRUSTED_ORIGINS = [f'https://{_railway_domain}'] if _railway_domain else []

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, conn_health_checks=True)
}