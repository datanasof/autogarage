# autogarage/settings.py
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Load /etc/autogarage.env if present
from dotenv import load_dotenv
load_dotenv("/etc/autogarage.env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-dev-key")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin","django.contrib.auth","django.contrib.contenttypes",
    "django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles",
    "rest_framework",
    "accounts","providers","appointments","reviews","core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "autogarage.subdomain_middleware.SubdomainMiddleware",
]

ROOT_URLCONF = "autogarage.urls"
WSGI_APPLICATION = "autogarage.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "autogarage"),
        "USER": os.getenv("DB_USER", "autogarage"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "sql_mode": "STRICT_TRANS_TABLES",
        }
    }
}

# Static files
STATICFILES_DIRS = [BASE_DIR / 'core' / 'static']
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static_collected"
# (If using WhiteNoise for dev convenience)
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}
}

# DRF (basic)
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
}

# Celery
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# Domain
BASE_DOMAIN = os.getenv("BASE_DOMAIN", "autogarage.local")
