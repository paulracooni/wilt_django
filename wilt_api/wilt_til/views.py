from django.http import Http404
from django.db.models import Q

from rest_framework import status
from rest_framework import mixins
from rest_framework import filters
from rest_framework import generics
from rest_framework import pagination

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view

from firebase_authentication import exceptions
from firebase_authentication import permissions

from wilt_til.models import Til, Clap, Bookmark
from wilt_til.serializers import TilSerializer
from wilt_til.serializers import ClapSerializer
from wilt_til.serializers import BookmarkSerializer

from firebase_admin import auth

__all__ = (
    "TilListCreate",
    "TilRetrieveUpdateDestroy",
    "TilBookmark",
)

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


class IsTilRealtedFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only lists is_public=True or user's instance
    """

    def filter_queryset(self, request, queryset, view):
        print(request.data)
        print(view)
        return queryset.filter(til=5)


# ////////////////////////////////////////////
# Define Pagination
# - [https://www.django-rest-framework.org/api-guide/pagination/]
# ////////////////////////////////////////////
class IdCursorPagination(pagination.CursorPagination):
    page_size = 15
    cursor_query_param = "id"
    ordering = "-date_created"


# ////////////////////////////////////////////
# Define views (generics)
# - [https://www.django-rest-framework.org/api-guide/generic-views/]
# ////////////////////////////////////////////
class TilListCreate(generics.ListCreateAPIView):
    queryset = Til.objects.all()
    serializer_class = TilSerializer
    pagination_class = IdCursorPagination
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


class TilBookmark(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    pagination_class = IdCursorPagination
    permission_classes = [permissions.IsMyself]
    filter_backends = [IsTilRealtedFilterBackend]

    def get(self, request, id, format=None):
        return self.list(self, request, id, format=None)

    def post(self, request, id, format=None):
        data = self.create(til=id, user=request.user.id)
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def delete(self, request, id, format=None):
        bookmark = self.get_bookmark_or_404(til=id, user=request.user.id)
        bookmark.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, til, user):
        serializer = self.get_serializer(data=dict(til=til, user=user))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def get_bookmark_or_404(self, **query):
        try:
            bookmark = self.get_queryset().get(**query)
        except Bookmark.DoesNotExist as ex:
            raise Http404
        return bookmark

    @staticmethod
    def get_success_headers(data):
        try:
            return {"Location": str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}
