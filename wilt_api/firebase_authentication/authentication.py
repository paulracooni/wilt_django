__all__ = "FirebaseAuthentication", "FirebaseAuthMiddleware", "firebase_app"

from django.conf import settings
from django.contrib.auth import get_user_model, middleware
from django.contrib.auth.models import AnonymousUser

import firebase_admin
import firebase_authentication
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
        # raise exceptions.InvalidAuthToken()
        return None
        
def get_or_anonymous(user_data):

    if user_data:
        user = UserModel.objects.get(id=user_data.get('uid'))
    else:
        user = AnonymousUser()
    
    return user

def is_anonymous(user):

        return isinstance(user, AnonymousUser)

class AuthenticationMixin:

    @staticmethod
    def get_auth_token(request):
        raise NotImplementedError()

    def authenticate(self, request):

        token = self.get_auth_token(request)
        user_data = verify_user_token(token)
        
        return get_or_anonymous(user_data)

class FirebaseAuthentication(AuthenticationMixin, authentication.BaseAuthentication):

    @staticmethod
    def get_auth_token(request):
        try:
            return request.META.get('HTTP_AUTHORIZATION')
        except Exception:
            raise exceptions.NoAuthToken()

    def authenticate(self, request):
        
        user = super(FirebaseAuthentication, self).authenticate(request)
        auth = None if is_anonymous(user) else "FirebaseAuth"

        return user, auth

    
class FirebaseAuthMiddleware(AuthenticationMixin, middleware.AuthenticationMiddleware):

    @staticmethod
    def get_auth_token(request):
        try:
            return request.META.get('HTTP_AUTHORIZATION')#request.COOKIES.get('access_token')
        except Exception:
            raise exceptions.NoAuthToken()

    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: self.authenticate(request))

