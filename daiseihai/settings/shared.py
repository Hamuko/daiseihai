"""
Django settings for daiseihai project.

Generated by 'django-admin startproject' using Django 2.0.7.
"""

import os
import raven

from django.core.exceptions import ImproperlyConfigured

try:
    from daiseihai.settings.local_settings import secrets
except ImportError:
    raise ImproperlyConfigured('Missing local_settings/secrets.py')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = secrets.SECRET_KEY

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'raven.contrib.django.raven_compat',
    'daiseihai',
    'daiseihai.archive',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'daiseihai.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': ['jinja2'],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'daiseihai.jinja2.environment'
        },
    },
]

WSGI_APPLICATION = 'daiseihai.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'localhost',
        'NAME': 'daiseihai',
        'USER': 'daiseihai',
        'PASSWORD': secrets.DATABASE_PASSWORD,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

RAVEN_CONFIG = {
    'dsn': '',
    'release': raven.fetch_git_sha(os.path.abspath(os.curdir)),
}

FILE_UPLOAD_PERMISSIONS = 0o644
