from rest_framework import status, mixins, generics, pagination

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.settings import api_settings

from wilt_backend import exceptions
from wilt_backend import permissions

from wilt_backend.utils import *
from wilt_backend.models import *
from wilt_backend.generics import *
from wilt_backend.serializers import *
from wilt_backend.views.helpers import *

from firebase_admin import auth

from ast import literal_eval

# ////////////////////////////////////////////
# Define views (generics)
# - [https://www.django-rest-framework.org/api-guide/generic-views/]
# ////////////////////////////////////////////


def parse_tag_and_create_if_new(tags):
    if isinstance(tags, str):
        tags = parse_tag_input(tags)
    for name in tags:
        Tag.objects.get_or_create(name=name)
    return tags


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
        instance = serializer.Meta.model.objects.get(id=serializer.data["id"])
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

        # Response
        instance = serializer.Meta.model.objects.get(id=serializer.data["id"])
        response_serializer = FeedSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

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
