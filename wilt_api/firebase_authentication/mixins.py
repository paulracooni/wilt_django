__all__ = "FirebaseAuthMixin",

from rest_framework.permissions import IsAuthenticated

from .authentication import FirebaseAuthentication


class FirebaseAuthMixin:
    permission_classes = IsAuthenticated,
    authentication_classes = FirebaseAuthentication,
