from django.http import Http404
from django.db.models import Q

from rest_framework import status
from rest_framework import filters
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from firebase_authentication import exceptions
from firebase_authentication import permissions

from wilt_til.models import Til, Clap, Bookmark
from wilt_til.serializers import TilSerializer

from firebase_admin import auth

__all__ = ("TilListCreate", "TilRetrieveUpdateDestroy")

# ////////////////////////////////////////////
# Define filters
# - [https://www.django-rest-framework.org/api-guide/filtering/]
# ////////////////////////////////////////////
class IsActiveFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only lists is_active=True instance
    """

    def filter_queryset(self, request, queryset, view):

        return queryset.filter(is_active=True)


class IsPublicOrMineFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only lists is_public=True or user's instance
    """

    def filter_queryset(self, request, queryset, view):
        if request.user.is_authenticated:
            query = Q(is_public=True) | Q(user=request.user.id)
        else:
            query = Q(is_public=True)
        return queryset.filter(query)


# ////////////////////////////////////////////
# Define views (generics)
# - [https://www.django-rest-framework.org/api-guide/generic-views/]
# ////////////////////////////////////////////
class TilListCreate(generics.ListCreateAPIView):
    queryset = Til.objects.all()
    serializer_class = TilSerializer
    permission_classes = [permissions.IsAuthor]
    filter_backends = [IsActiveFilterBackend, IsPublicOrMineFilterBackend]


class TilRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Til.objects.all()
    serializer_class = TilSerializer
    permission_classes = [permissions.IsAuthor]
    lookup_field = "id"

    def perform_destroy(self, instance):
        serializer = self.get_serializer(
            instance, data=dict(is_active=False), partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
