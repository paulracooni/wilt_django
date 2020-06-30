__all__ = "FirebaseAuthentication", "FirebaseAuthMiddleware", "firebase_app"

from django.conf import settings
from django.contrib.auth import get_user_model, middleware

import firebase_admin
from django.utils.functional import SimpleLazyObject
from firebase_admin import auth
from rest_framework import authentication, exceptions

from . import exceptions

UserModel = get_user_model()
credentials = firebase_admin.credentials.Certificate(settings.FIREBASE_PATH)
firebase_app = firebase_admin.initialize_app(credentials)


def verify_user_token(token):
    try:
        return auth.verify_id_token(token)
    except Exception:
        raise exceptions.InvalidAuthToken()


def get_or_create_user(user_data):
    user, created = UserModel.objects.get_or_create(
        id=user_data.get('uid'),
        defaults={"email": user_data.get('email')}
    )
    return user


class AuthenticationMixin:

    @staticmethod
    def get_auth_token(request):
        raise NotImplementedError()

    def authenticate(self, request):
        token = self.get_auth_token(request)
        user_data = verify_user_token(token)
        return get_or_create_user(user_data)


class FirebaseAuthentication(AuthenticationMixin, authentication.BaseAuthentication):

    @staticmethod
    def get_auth_token(request):
        try:
            return request.META.get('HTTP_AUTHORIZATION')
        except Exception:
            raise exceptions.NoAuthToken()

    def authenticate(self, request):
        user = super(FirebaseAuthentication, self).authenticate(request)
        return user, None


class FirebaseAuthMiddleware(AuthenticationMixin, middleware.AuthenticationMiddleware):

    @staticmethod
    def get_auth_token(request):
        try:
            return request.COOKIES.get('access_token')
        except Exception:
            raise exceptions.NoAuthToken()

    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: self.authenticate(request))
