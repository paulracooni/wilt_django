from django.db.models import Q

from rest_framework import status
from rest_framework import mixins
from rest_framework import filters
from rest_framework import generics
from rest_framework import pagination

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.settings import api_settings

from firebase_authentication import exceptions
from firebase_authentication import permissions

from wilt_til.models import Til, Clap, Bookmark, Tag  # , TilTag
from wilt_til.generics import TilRelationAPIView
from wilt_til.serializers import TilSerializer
from wilt_til.serializers import ClapSerializer
from wilt_til.serializers import BookmarkSerializer
from wilt_til.utils import parse_tag_input
from firebase_admin import auth

import tagging

from ast import literal_eval

__all__ = ("TilListCreate", "TilRetrieveUpdateDestroy", "TilBookmark", "TilClap")


# ////////////////////////////////////////////
# Define filters
# - [https://www.django-rest-framework.org/api-guide/filtering/]
# ////////////////////////////////////////////
class IsActiveFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only lists is_active=True instance
    """

    def filter_queryset(self, request, queryset, view):
        # @TODO: You must delete this condtion if admin page will implementd.
        if request.method == "PATCH":
            return queryset
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
    Filter that only lists Til related
    """

    def filter_queryset(self, request, queryset, view):
        # til_id must be initilized before call ListModelMixin.list
        return queryset.filter(til=view.til_id)


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
def extract_data_with_user_id_form(request):
    data = dict(request.data.items())
    data["user"] = request.user.id
    return data


def parse_tag_and_create_if_new(tags):

    if isinstance(tags, str):
        tags = parse_tag_input(tags)
    for name in tags:
        Tag.objects.get_or_create(name=name)

    return tags


def get_success_headers(data):
    try:
        return {"Location": str(data[api_settings.URL_FIELD_NAME])}
    except (TypeError, KeyError):
        return {}


class TilListCreate(generics.GenericAPIView):
    """
    [GET]
    - List all api
    [POST]
    - Create New Til
    """

    queryset = Til.objects.all()
    serializer_class = TilSerializer
    pagination_class = IdCursorPagination
    permission_classes = [permissions.IsAuthor]
    filter_backends = [IsActiveFilterBackend, IsPublicOrMineFilterBackend]

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        data = extract_data_with_user_id_form(request)
        data["tags"] = parse_tag_and_create_if_new(data.get("tags", ""))
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class TilRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Til.objects.all()
    serializer_class = TilSerializer
    permission_classes = [permissions.IsAuthor]
    filter_backends = [IsActiveFilterBackend, IsPublicOrMineFilterBackend]
    lookup_field = "id"

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        data = dict(request.data.items())
        data["tags"] = parse_tag_and_create_if_new(data.get("tags", ""))

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_destroy(self, instance):
        serializer = self.get_serializer(
            instance, data=dict(is_active=False), partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)


class TilBookmark(TilRelationAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    pagination_class = IdCursorPagination
    permission_classes = [permissions.IsMyself]
    filter_backends = [IsTilRealtedFilterBackend]


class TilClap(TilRelationAPIView):
    queryset = Clap.objects.all()
    serializer_class = ClapSerializer
    pagination_class = IdCursorPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [IsTilRealtedFilterBackend]
