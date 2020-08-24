"""
Django settings for wilt_api project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from .s3_password import ACCESSS_KEY_ID, SECRET_ACCESS_KEY, REGION, STORAGE_BUCKET_NAME

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "4!08cn51p7x^n7!mswe=_g51*#$d70xznx5q0z(yf45l*jm#)k"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DEVELOP_CODE = "Hey! I'm Cool Developer!"
ADMIN_USER_ID = "g0iZyb7rMOge8tlgvGJIPU4sUE03"
APPEND_SLASH = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    
    "wilt_backend",
    "wilt_policy",
    "fcm_manager",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    "wilt_backend.authentication.FirebaseAuthMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "wilt_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "wilt_api.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"

# REST settings

## Firebase authentication settings
FIREBASE_PATH = os.path.join(BASE_DIR, "../..", "firebase_key.json")
AUTH_USER_MODEL = "wilt_backend.WiltUser"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # The default authentication schemes may be set globally.
        "wilt_backend.authentication.FirebaseAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
}


###########################AWS
AWS_ACCESS_KEY_ID = ACCESSS_KEY_ID
AWS_SECRET_ACCESS_KEY = SECRET_ACCESS_KEY
AWS_REGION = REGION

AWS_DEFAULT_ACL = "public-read"
AWS_S3_HOST = "s3.%s.amazonaws.com"

###S3 Storages
AWS_STORAGE_BUCKET_NAME = STORAGE_BUCKET_NAME  # 설정한 버킷 이름

AWS_S3_CUSTOM_DOMAIN = "s3.%s.amazonaws.com/%s" % (AWS_REGION, AWS_STORAGE_BUCKET_NAME)
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

## Markdownify settings
MARKDOWNIFY_STRIP = False
MARKDOWNIFY_WHITELIST_TAGS = {
    "a",
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "h7",
    "ul",
    "li",
    "span",
}
