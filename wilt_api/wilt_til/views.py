from django.db.models import Q

from rest_framework import status
from rest_framework import mixins
from rest_framework import filters
from rest_framework import generics
from rest_framework import pagination

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from firebase_authentication import exceptions
from firebase_authentication import permissions

from wilt_til.models import Til, Clap, Bookmark, Tag, TilTag
from wilt_til.generics import TilRelationAPIView
from wilt_til.serializers import TilSerializer
from wilt_til.serializers import ClapSerializer
from wilt_til.serializers import BookmarkSerializer

from firebase_admin import auth

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
class TilListCreate(generics.ListCreateAPIView):
    queryset = Til.objects.all()
    serializer_class = TilSerializer
    pagination_class = IdCursorPagination
    permission_classes = [permissions.IsAuthor]
    filter_backends = [IsActiveFilterBackend, IsPublicOrMineFilterBackend]

    def create(self, request, *args, **kwargs):

        
        data = self.__put_user_id_data(request)
        
        # extracting tag_list
        tag_list = data.get("tag_list", [])

        if tag_list:
            # If tag_list in data, Evaluate tag_list string into List
            # @TODO: We should check type and list element type constraint! 
            # @TODO: - Tag_list must be list, list element must be string.
            # [HINT]: If literal_eval get unexpected string, Raise SyntaxError
            tag_list = literal_eval(tag_list)
            data.pop("tag_list")

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if tag_list:
            til_id = serializer.data.get('id', None)
            til = self.get_queryset().get(id=til_id)
            self.create_tag_and_tiltag(til, tag_list)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @staticmethod
    def __put_user_id_data(request):
        data = dict(request.data.items())
        data["user"] = request.user.id
        return data

    @staticmethod
    def create_tag_and_tiltag(til, tag_list):
        """
        til과 해당 til의 tag_list를 받아서 저장하는 함수
        :param til: object
        :param tag_list: ['피그마', '제플린']
        :return:
        """
        for tag in tag_list:
            try:
                tag = Tag.objects.get(name=tag)
            except Tag.DoesNotExist:
                tag = Tag.objects.create(name=tag)

            TilTag.objects.create(til=til, tag_name=tag)

        return True


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
