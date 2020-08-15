from .production_password import NAME, USER, PASSWORD, HOST
from .settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": NAME,
        "USER": USER,
        "PASSWORD": PASSWORD,
        "HOST": HOST,
        "PORT": "3306",
        "CONN_MAX_AGE": 600,
        "OPTIONS": {
            "init_command": "SET default_storage_engine=INNODB, character_set_connection=utf8mb4, collation_connection=utf8mb4_unicode_ci",
            "charset": "utf8mb4",
        },
    },
}
