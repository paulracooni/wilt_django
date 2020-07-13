# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
from .settings import *
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'wilt_db',
#         'USER': 'root',
#         'PASSWORD': 'wilt',
#         'HOST': '127.0.0.1',
#         'PORT': '4404',
#         'CONN_MAX_AGE': 600,
#         'OPTIONS': {
#             'init_command': 'SET default_storage_engine=INNODB, character_set_connection=utf8mb4, collation_connection=utf8mb4_unicode_ci',
#             'charset':'utf8mb4',
#         },
#     },
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
