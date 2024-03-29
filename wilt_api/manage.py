#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

CASE_ = dict(
    development="wilt_api.settings.development",
    test="wilt_api.settings.test",
    production="wilt_api.settings.production",
)


def main():
    WILT_ENV = os.environ.get("WILT_ENV", "development")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", CASE_[WILT_ENV])

    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wilt_api.settings")

    print("manage WILT ENV: {}".format(WILT_ENV))

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
