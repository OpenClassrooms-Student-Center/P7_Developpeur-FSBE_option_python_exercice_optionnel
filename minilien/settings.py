"""Configuration Django de MiniLien."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-7k#p2v!x9m@q4w$e8r(t6y)u1i&o3p"
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS = [
    "links",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "minilien.urls"
WSGI_APPLICATION = "minilien.wsgi.application"

# Les liens sont stockés en mémoire : pas de base de données.
DATABASES = {}

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = False
USE_TZ = True
APPEND_SLASH = False

# Adresse publique utilisée pour construire les liens courts
MINILIEN_BASE_URL = "http://localhost:8080"

# Jeton exigé dans l'en-tête X-Admin-Token pour supprimer un lien
MINILIEN_ADMIN_TOKEN = "minilien-admin-2024"
