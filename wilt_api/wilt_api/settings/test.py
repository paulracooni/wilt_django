from .test_password import NAME, USER, PASSWORD, HOST, PORT
from . import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": NAME,
        "USER": USER,
        "PASSWORD": PASSWORD,
        "HOST": HOST,
        "PORT": PORT,
        "CONN_MAX_AGE": 600,
        "OPTIONS": {
            "init_command": "SET default_storage_engine=INNODB, character_set_connection=utf8mb4, collation_connection=utf8mb4_unicode_ci",
            "charset": "utf8mb4",
        },
    },
}
