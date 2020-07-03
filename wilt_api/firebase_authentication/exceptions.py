__all__ = "NoAuthToken", "InvalidAuthToken", "UserNotFound",

from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException

class NoAuthToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('No id token provided.')
    default_code = 'no_auth_token'


class InvalidIdAuthToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Invalid id token provided.')
    default_code = 'invalid_token'


class ExpiredIdAuthToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Expired id token provided.')
    default_code = 'expired_token'


class RevokedIdAuthToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Revoked id token provided.')
    default_code = 'revoked_token'


class UserNotFound(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("User with provided Firebase UID not found.")
    default_code = 'user_not_found'


class UserEmailNotMatched(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("User email and uid is not matched.")
    default_code = 'user_not_found'
