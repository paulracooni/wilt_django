from django.conf import settings
from django.contrib.auth import get_user_model, middleware
from django.contrib.auth.models import AnonymousUser, update_last_login

import firebase_admin
import firebase_authentication
from django.utils.functional import SimpleLazyObject

from django.contrib.auth import get_user

from firebase_admin import auth
from rest_framework import authentication, exceptions

from wilt_backend import exceptions
from wilt_backend.models import WiltUser

from wilt_api.settings import DEBUG, DEVELOP_CODE, ADMIN_USER_ID

UserModel = get_user_model()
credentials = firebase_admin.credentials.Certificate(settings.FIREBASE_PATH)
firebase_app = firebase_admin.initialize_app(credentials)


def verify_user_token(token):

    try:
        return auth.verify_id_token(token, check_revoked=True)
    except auth.RevokedIdTokenError:
        raise exceptions.RevokedIdToken()
    except auth.ExpiredIdTokenError:
        raise exceptions.ExpiredIdToken()
    except auth.InvalidIdTokenError as ex:
        raise exceptions.InvalidIdToken()
    except ValueError:
        pass

    return None


def get_or_anonymous(user_data):

    if is_anonymous(user_data):
        user = AnonymousUser()
    else:
        user = get_or_create_user(user_data)

    return user


def is_anonymous(user_data):

    if user_data == None:
        return True

    provider = user_data["firebase"]["sign_in_provider"]
    return provider == "anonymous"


def get_or_create_user(user_data):

    user, created = WiltUser.objects.get_or_create(
        id=user_data.get("uid"),
        defaults=dict(
            email=user_data.get("email", None), display_name=None, picture=None
        ),
    )  # WiltUser.objects.get_or_create

    # Update user picture it no picture
    if not created and user.picture == None:
        setattr(user, "picture", user_data.get("picture", None))
        user.save()

    update_last_login(None, user)

    return user


class AuthenticationMixin:
    @staticmethod
    def get_auth_token(request):
        raise NotImplementedError()

    def authenticate(self, request):

        # For Staff User on Admin page
        user = get_user(request)
        if user and user.is_staff:
            return user

        # For DEVELOPER
        token = self.get_auth_token(request)
        if DEBUG and token == DEVELOP_CODE:
            user = WiltUser.objects.get(id=ADMIN_USER_ID)
            return user

        # For Wilt User and Anonymous User
        user_data = verify_user_token(token)
        user = get_or_anonymous(user_data)

        return user


class FirebaseAuthentication(AuthenticationMixin, authentication.BaseAuthentication):
    @staticmethod
    def get_auth_token(request):
        try:
            return request.META.get("HTTP_AUTHORIZATION")
        except Exception:
            raise exceptions.NoAuthToken()

    def authenticate(self, request):
        user = super(FirebaseAuthentication, self).authenticate(request)
        auth = None if isinstance(user, AnonymousUser) else "FirebaseAuth"
        return user, auth


class FirebaseAuthMiddleware(AuthenticationMixin, middleware.AuthenticationMiddleware):
    @staticmethod
    def get_auth_token(request):
        try:
            return request.META.get("HTTP_AUTHORIZATION")
        except Exception:
            raise exceptions.NoAuthToken()

    def process_request(self, request):

        request.user = SimpleLazyObject(lambda: self.authenticate(request))
