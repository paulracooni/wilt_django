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


def attach_did_something(data, user_id):
    def attach(data, user_id):
        til_id = data.get("id")
        if user_id is not None:
            did_something = dict(
                did_clap=Clap.objects.filter(user=user_id, til=til_id).exists(),
                did_bookmark=Bookmark.objects.filter(user=user_id, til=til_id).exists(),
            )
        else:
            did_something = dict(did_clap=False, did_bookmark=False,)
        data.update(did_something)
        return data

    if isinstance(data, dict):
        data = attach(data, user_id)
    else:
        data = [attach(element, user_id) for element in data]
    return data


class FeedListCreate(MixInTilQuery, APIView):
    permission_classes = [permissions.IsAuthorOrAllowAnonymousGet]

    def get(self, request, *args, **kwargs):

        # Initialize filter and queryset
        filters = self.build_filter_initial()
        filters.update(self.build_filter_etc())
        queryset = Til.objects.filter(**filters)

        # Searching
        q_search = self.build_q_search()
        queryset = queryset.filter(q_search)

        # Pagenation
        paginator = IdCursorPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        queryset = page if page is not None else queryset

        # Serializing
        serializer = FeedSerializer(queryset, many=True)

        # Attach additional info (it can't be attached by serializer)
        response_data = attach_did_something(
            data=serializer.data, user_id=getattr(request.user, "id", None)
        )

        if page is not None:
            response = paginator.get_paginated_response(response_data)
        else:
            response = Response(response_data, status=status.HTTP_200_OK)

        return response

    def post(self, request, *args, **kwargs):
        # Save
        data = self.extract_data_with_user_id_from(request)
        data["tags"] = parse_tag_and_create_if_new(data.get("tags", ""))
        serializer = TilSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Response
        instance = serializer.Meta.model.objects.get(id=serializer.data["id"])
        response_serializer = FeedSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def extract_data_with_user_id_from(request):
        data = dict(request.data.items())
        if "user" not in data.keys() and hasattr(request.user, "id"):
            data["user"] = getattr(request.user, "id", None)
        return data


class TilRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Til.objects.all()
    serializer_class = TilSerializer
    permission_classes = [permissions.IsAuthor]
    filter_backends = [IsActiveFilterBackend, IsPublicOrMineFilterBackend]
    lookup_field = "id"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = FeedSerializer(instance)
        response_data = attach_did_something(
            data=serializer.data, user_id=getattr(request.user, "id", None)
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
    serializer_class_userinfo = BookmarkUserInfoSerializer
    pagination_class = IdCursorPagination
    permission_classes = [permissions.IsMyself]
    filter_backends = [IsTilRealtedFilterBackend]


class TilClap(TilRelationAPIView):
    queryset = Clap.objects.all()
    serializer_class = ClapSerializer
    serializer_class_userinfo = ClapUserInfoSerializer
    pagination_class = IdCursorPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [IsTilRealtedFilterBackend]


class TilComment(TilRelationAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    serializer_class_userinfo = CommentUserInfoSerializer
    pagination_class = IdCursorPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [IsTilRealtedFilterBackend, IsActiveFilterBackend]

    def delete(self, request, til_id, format=None):
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TilCommentUpdateDestroy(APIView):
    permission_classes = [permissions.IsMyself]
    NO_UPDATE_FIELD = ("is_active",)

    def patch(self, request, til_id, comment_id, format=None):
        comment = self.retrive_comment_or_false(comment_id)
        if comment:
            response = self.update(comment, request.data, partial=True)
        else:
            response = self.get_fail_response(til_id, comment_id)
        return response

    def delete(self, request, til_id, comment_id, format=None):
        comment = self.retrive_comment_or_false(comment_id)
        if comment:
            serializer = self.__update(comment, dict(is_active=False), partial=True)
            detail = f"Comment({comment_id}) is deleted."
            response = Response(dict(detail=detail), status=status.HTTP_204_NO_CONTENT)
        else:
            response = self.get_fail_response(til_id, comment_id)
        return response

    def update(self, comment, data, partial=True):
        # Update comment
        fields = self.__filter_fields(data)
        serializer = self.__update(comment, fields, partial=partial)

        # Retrive comment with user info
        updated_commnet = self.retrive_comment_or_false(comment.id)
        serializer = CommentUserInfoSerializer(updated_commnet)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @staticmethod
    def __update(comment, data, partial=False):
        serializer = CommentSerializer(comment, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer

    @staticmethod
    def retrive_comment_or_false(comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
        except exceptions.ObjectDoesNotExist as ex:
            return False
        return comment

    @staticmethod
    def get_fail_response(til_id, comment_id):
        detail = dict(detail=f"bad request til:{til_id}, comment:{comment_id}")
        return Response(detail, status=status.HTTP_400_BAD_REQUEST)

    @classmethod
    def __filter_fields(cls, fields):
        fields = {
            field_name: field_value
            for field_name, field_value in fields.items()
            if field_name not in cls.NO_UPDATE_FIELD
        }
        return fields
