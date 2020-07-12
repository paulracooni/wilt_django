from django.db.models import Q
from django.http import Http404

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
from wilt_til.serializers import FeedSerializer
from wilt_til.serializers import ClapSerializer
from wilt_til.serializers import BookmarkSerializer
from wilt_til.utils import parse_tag_input
from firebase_admin import auth

import tagging

from ast import literal_eval

__all__ = (
    "TilListCreate",
    "TilRetrieveUpdateDestroy",
    "TilBookmark",
    "TilClap",
    "IdCursorPagination",
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


class TilSearchingFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):

        valid_query_params = self.filter_valid_query(
            model=queryset.model, query_params=request.query_params
        )

        if valid_query_params:
            query = self.build_query(valid_query_params)
            queryset = queryset.filter(**query)

        return queryset

    def filter_valid_query(self, model, query_params):
        valid_query = dict(
            [(key, val) for key, val in query_params.items() if hasattr(model, key)]
        )
        return valid_query

    def build_query(self, query_params):
        query = dict()
        for key, val in query_params.items():
            if key == "tags":
                query["tags__in"] = self.__get_tags(val)
            else:
                query[key] = val

        return query

    def __get_tags(self, tags):
        instances = []
        for name in parse_tag_input(tags):
            try:
                instances.append(Tag.objects.get(name=name))
            except Tag.DoesNotExist:
                pass

        return instances


# ////////////////////////////////////////////
# Define Pagination
# - [https://www.django-rest-framework.org/api-guide/pagination/]
# ////////////////////////////////////////////
class IdCursorPagination(pagination.CursorPagination):
    page_size = 15
    cursor_query_param = "cursor"
    ordering = "-date_created"


# ////////////////////////////////////////////
# Define Helper functions for APIViews
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


def attach_additional_data(data, user_id):
    def attach(data, user_id):
        til_id = data.get("id")
        if user_id is not None:
            additional_data = dict(
                did_clap=Clap.objects.filter(user=user_id, til=til_id).exists(),
                did_bookmark=Bookmark.objects.filter(user=user_id, til=til_id).exists(),
            )
        else:
            additional_data = dict(did_clap=False, did_bookmark=False,)
        data.update(additional_data)
        return data

    if isinstance(data, dict):
        data = attach(data, user_id)
    else:
        data = [attach(element, user_id) for element in data]

    return data


# ////////////////////////////////////////////
# Define views (generics)
# - [https://www.django-rest-framework.org/api-guide/generic-views/]
# ////////////////////////////////////////////


class FeedListCreate(generics.GenericAPIView):
    queryset = Til.objects.all()
    serializer_class = FeedSerializer
    pagination_class = IdCursorPagination
    permission_classes = [permissions.IsAuthor]
    filter_backends = [
        IsActiveFilterBackend,
        IsPublicOrMineFilterBackend,
        TilSearchingFilterBackend,
    ]

    def get(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        queryset = page if page is not None else queryset

        serializer = self.get_serializer(queryset, many=True)

        response_data = attach_additional_data(
            data=serializer.data, user_id=request.user.id
        )

        if page is not None:
            response = self.get_paginated_response(response_data)
        else:
            response = Response(response_data, status=status.HTTP_200_OK)

        return response

    def post(self, request, *args, **kwargs):
        # Save 
        data = extract_data_with_user_id_form(request)
        data["tags"] = parse_tag_and_create_if_new(data.get("tags", ""))
        serializer = TilSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Response
        instance = serializer.Meta.model.objects.get(id=serializer.data['id'])
        response_serializer = self.get_serializer(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class TilRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Til.objects.all()
    serializer_class = TilSerializer
    permission_classes = [permissions.IsAuthor]
    filter_backends = [IsActiveFilterBackend, IsPublicOrMineFilterBackend]
    lookup_field = "id"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = FeedSerializer(instance)
        response_data = attach_additional_data(
            data=serializer.data, user_id=request.user.id
        )
        return Response(response_data, status=status.HTTP_200_OK)

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

        return Response(serializer.data, status=status.HTTP_200_OK)

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
