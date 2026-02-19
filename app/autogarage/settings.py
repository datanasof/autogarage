
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY','dev-insecure')
DEBUG = os.environ.get('DJANGO_DEBUG','True')=='True'
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS','localhost,127.0.0.1,[::1]').split(',') if h.strip()]
BASE_DOMAIN = os.environ.get('BASE_DOMAIN','localhost')

INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
    'rest_framework',
    'accounts','providers','appointments','reviews','core'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'autogarage.subdomain_middleware.SubdomainProviderMiddleware',
]

ROOT_URLCONF = 'autogarage.urls'
TEMPLATES = [{
    'BACKEND':'django.template.backends.django.DjangoTemplates',
    'DIRS':[BASE_DIR / 'core' / 'templates'],
    'APP_DIRS':True,
    'OPTIONS':{'context_processors':[
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'core.context.google_maps_api_key',
    ]}
}]
WSGI_APPLICATION = 'autogarage.wsgi.application'
ASGI_APPLICATION = 'autogarage.asgi.application'

if os.environ.get('DB_NAME'):
    DATABASES={'default':{
        'ENGINE':'django.db.backends.mysql',
        'NAME':os.environ.get('DB_NAME','autogarage'),
        'USER':os.environ.get('DB_USER','autogarage'),
        'PASSWORD':os.environ.get('DB_PASSWORD',''),
        'HOST':os.environ.get('DB_HOST','127.0.0.1'),
        'PORT':os.environ.get('DB_PORT','3306'),
        'OPTIONS':{'charset':'utf8mb4'}
    }}
else:
    DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}

AUTH_USER_MODEL = 'accounts.User'
LANGUAGE_CODE='en-us'
TIME_ZONE='UTC'
USE_I18N=True
USE_TZ=True
STATIC_URL='/static/'
STATIC_ROOT=BASE_DIR/'static_collected'
STATICFILES_DIRS=[BASE_DIR/'core'/'static']
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'

REST_FRAMEWORK={
    'DEFAULT_AUTHENTICATION_CLASSES':['rest_framework.authentication.SessionAuthentication','rest_framework.authentication.BasicAuthentication'],
    'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.IsAuthenticatedOrReadOnly']
}

EMAIL_BACKEND=os.environ.get('EMAIL_BACKEND','django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST=os.environ.get('EMAIL_HOST','')
EMAIL_PORT=int(os.environ.get('EMAIL_PORT','25') or 25)
EMAIL_HOST_USER=os.environ.get('EMAIL_HOST_USER','')
EMAIL_HOST_PASSWORD=os.environ.get('EMAIL_HOST_PASSWORD','')
EMAIL_USE_TLS=os.environ.get('EMAIL_USE_TLS','False')=='True'
DEFAULT_FROM_EMAIL=os.environ.get('EMAIL_FROM','no-reply@localhost')

REDIS_URL=os.environ.get('REDIS_URL','redis://127.0.0.1:6379/0')
CELERY_BROKER_URL=REDIS_URL
CELERY_RESULT_BACKEND=REDIS_URL
GOOGLE_MAPS_API_KEY=os.environ.get('GOOGLE_MAPS_API_KEY','')
