__all__ = "NoAuthToken", "InvalidAuthToken", "UserNotFound",

from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException


class NoAuthToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('No authentication token provided.')
    default_code = 'no_auth_token'


class InvalidAuthToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Invalid authentication token provided.')
    default_code = 'invalid_token'


class UserNotFound(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("User with provided Firebase UID not found.")
    default_code = 'user_not_found'
