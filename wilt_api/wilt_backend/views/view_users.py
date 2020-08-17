from django.db.models import Count, Sum
from django.http import QueryDict

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
from wilt_backend.views.view_tils import attach_did_something
from firebase_admin import auth

from ast import literal_eval


def get_user_or_false(id):
    try:
        user = WiltUser.objects.get(id=id)
    except WiltUser.DoesNotExist as ex:
        return False
    return user


def get_active_user_or_false(id):
    user = get_user_or_false(id)
    if user and not user.is_active:
        return False
    return user


def get_invalid_user_response(id):
    detail = f"Invalid user id({id})."
    return Response(dict(detail=detail), status=status.HTTP_404_NOT_FOUND)


class UserDetail(APIView):

    permission_classes = [permissions.IsMyself]
    NO_UPDATE_FIELD = ("id", "email", "is_staff", "is_superuser")

    def get(self, request, user_id, format=None):
        active_user = get_active_user_or_false(id=user_id)
        if active_user:
            serializer = WiltUserSerializer(active_user)
            response = Response(serializer.data, status=status.HTTP_200_OK)
        else:
            detail = "Deleted user. (is_active=False)"
            response = Response(dict(detail=detail), status=status.HTTP_204_NO_CONTENT)
        return response

    def put(self, request, user_id, format=None):
        user = get_user_or_false(id=user_id)
        if user:
            response = self.update(user, request.data, partial=False)
        else:
            response = self.get_invalid_user(user_id)
        return response

    def patch(self, request, user_id, format=None):
        user = get_user_or_false(id=user_id)
        if user:
            if type(request.data) is dict:
                user_info = request.data
            else:
                user_info = request.data.dict()

            if "career_year" in user_info:
                if not user_info["career_year"]:
                    user_info["career_year"] = None

            modify_data = QueryDict("", mutable=True)
            modify_data.update(user_info)
            response = self.update(user, modify_data, partial=True)
        else:
            response = get_invalid_user_response(user_id)
        return response

    def delete(self, request, user_id, format=None):
        user = get_user_or_false(id=user_id)
        if user:
            serializer = self.__update(user, dict(is_active=False), partial=True)
            detail = f"User({user_id}) is deleted."
            response = Response(dict(detail=detail), status=status.HTTP_204_NO_CONTENT)
        else:
            response = get_invalid_user_response(user_id)
        return response

    def update(self, user, data, partial=True):
        fields = self.__filter_fields(data)
        serializer = self.__update(user, fields, partial=partial)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @staticmethod
    def __update(user, data, partial=False):
        serializer = WiltUserSerializer(user, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer

    @classmethod
    def __filter_fields(cls, fields):
        fields = {
            field_name: field_value
            for field_name, field_value in fields.items()
            if field_name not in cls.NO_UPDATE_FIELD
        }
        return fields


class UserCheck(APIView):

    # permission_classes = [permissions.IsAuthenticated]
    def get(self, request, format=None):
        """
        List all user
        - This will be depreciated
        """
        users = WiltUser.objects.all()
        serializer = WiltUserSerializer(users, many=True)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        return response

    def post(self, request, format=None):
        """
        Check is unused display_name
        """
        if self.__is_not_display_name_in(request):
            response = Response(
                dict(detail="Must include display_name in Body."),
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            response = Response(
                dict(is_not_used=self.__is_not_used_display_name(request)),
                status=status.HTTP_200_OK,
            )
        return response

    @staticmethod
    def __is_not_display_name_in(request):
        return "display_name" not in request.data.keys()

    @staticmethod
    def __is_not_used_display_name(request):
        try:
            display_name = request.data["display_name"]
            display_name = WiltUser.objects.normalize_display_name(display_name)
            WiltUser.objects.get(display_name=display_name)
            is_not_used = False
        except WiltUser.DoesNotExist:
            is_not_used = True

        return is_not_used


# User의 TIL을 clap한 사람들에 대한 정보를 불러오는 view
class UserClaps(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id, format=None):

        active_user = get_active_user_or_false(id=user_id)
        if active_user:
            # Query data
            queryset = Til.objects.filter(user=active_user, is_active=True, is_public=True)
            queryset = Clap.objects.filter(til__in=[query.id for query in queryset])

            # Pagenation
            paginator = IdCursorPagination()
            queryset = paginator.paginate_queryset(queryset, request, view=self)
            serializer = ClapUserInfoSerializer(queryset, many=True)

            # Attach did somthing data
            response_data = attach_did_something(
                data=serializer.data, user_id=active_user.id
            )

            # Response data
            response = paginator.get_paginated_response(response_data)
        else:
            response = get_invalid_user_response(id=user_id)
        return response


# User가 북마크한 Til 목록을 불러오는 view
class UserBookmark(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id, format=None):

        active_user = get_active_user_or_false(id=user_id)
        if active_user:
            # Query data
            queryset = Bookmark.objects.select_related("til").filter(user=active_user)
            queryset = Til.objects.filter(id__in=[query.til.id for query in queryset])
            queryset = queryset.filter(is_active=True, is_public=True)

            # Pagenation
            paginator = IdCursorPagination()
            queryset = paginator.paginate_queryset(queryset, request, view=self)
            serializer = FeedSerializer(queryset, many=True)

            # Attach did somthing data
            response_data = attach_did_something(
                data=serializer.data, user_id=active_user.id
            )

            # Response data
            response = paginator.get_paginated_response(response_data)
        else:
            response = get_invalid_user_response(id=user_id)
        return response


# User가 TIL에 사용하였던 태그들을 불러오는 view
class UserTag(MixInTilQuery, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id, format=None):

        active_user = get_active_user_or_false(id=user_id)
        if active_user:
            tags = request.GET.get("tags", "")
            response = self.__count_tags_by(active_user)
        else:
            response = get_invalid_user_response(id=user_id)
        return response

    def __count_tags_by(self, active_user):
        # Query data
        queryset = Til.objects.filter(
            user=active_user, is_active=True
        ).prefetch_related("tags")

        # Count tags
        tags_count = dict()
        for til in queryset:
            for tag in til.tags.all():
                if tag.name in tags_count.keys():
                    tags_count[tag.name] += 1
                else:
                    tags_count[tag.name] = 1

        # Response data
        response = Response(tags_count, status=status.HTTP_200_OK)
        return response


# 유저의 TIL을 가져오는 view
# 페이지 네이션 적용 필
class UserTils(MixInTilQuery, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id, format=None):

        active_user = get_active_user_or_false(id=user_id)
        if active_user:

            # Initialize filter and queryset
            filters = dict(user=active_user, is_active=True)
            if active_user.id != request.user.id:
                filters.update(is_public=True)
            filters.update(self.build_filter_etc())
            queryset = Til.objects.filter(**filters)

            # Searching
            q_search = self.build_q_search()
            queryset = queryset.filter(q_search)

            # Pagenation
            paginator = IdCursorPagination()
            page = paginator.paginate_queryset(queryset, request, view=self)
            queryset = page if page is not None else queryset
            serializer = FeedSerializer(queryset, many=True)

            # Attach did somthing data
            response_data = attach_did_something(
                data=serializer.data, user_id=active_user.id
            )

            # Response data
            response = paginator.get_paginated_response(response_data)

        else:
            response = get_invalid_user_response(id=id)

        return response


class UserCategories(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id, format=None):

        active_user = get_active_user_or_false(id=user_id)
        if active_user:
            query_set = (
                Til.objects.filter(user=active_user, is_active=True)
                .values_list("category", flat=True)
                .distinct()
            )

            query_set_v2 = (
                Til.objects.filter(user=active_user, is_active=True)
                .values("category")
                .annotate(count=Count('category'))
            )

            data = dict(
                categories=[category for category in query_set],
                categories_count = [category for category in query_set_v2]
            )
            response = Response(data, status=status.HTTP_200_OK)
        else:
            response = get_invalid_user_response(id=id)
        return response


# 유저의 til 갯수/ 응원 갯수 / 북마크 갯수를 불러오는 view
class UserTotalCount(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id, format=None):
        result = dict()
        active_user = get_active_user_or_false(id=user_id)

        if active_user:
            # 유저의 til 갯수
            user_til_count = Til.objects.filter(
                user=active_user, is_active=True
            ).count()

            # 유저의 응원 갯수
            user_clap_count = Clap.objects.filter(
                til__user=active_user, til__is_active=True
            ).count()

            # 유저의 북마크 갯수
            user_bookmark_count = Bookmark.objects.filter(
                user=active_user, til__is_active=True
            ).count()

            result["user_til_count"] = user_til_count
            result["user_clap_count"] = user_clap_count
            result["user_bookmark_count"] = user_bookmark_count

            response = Response(result, status=status.HTTP_200_OK)
        else:
            response = get_invalid_user_response(id=user_id)

        return response


# /////////////////////////////////////////////////
# Following, Followers related views
# /////////////////////////////////////////////////
class UserFollowers(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = UserFollow.objects.all()
    serializer_class = UserFollowSerializer
    # pagination_class
    # permission_classes
    # filter_backends


class UserFollowing(MixInFollowList, generics.GenericAPIView):
    queryset = UserFollow.objects.all()
    serializer_class = UserFollowSerializer
    serializer_class_user_info = UserFollowingSerializer
    pagination_class = IdCursorPagination
    # permission_classes
    filter_backends = [IsFollowingFilterBackend]

    def get(self, request, user_id, format=None):
        return_count = bool(request.query_params.get("return_count", 0))
        if return_count:
            count = self.get_queryset().filter(user_id=request.user.id).count()
            return Response(dict(count=count), status=status.HTTP_200_OK)
        return self.list(request)

    def post(self, request, user_id, format=None):
        data = self.create(
            data=dict(user_id=request.user.id, following_user_id=user_id)
        )
        return Response(data, status=status.HTTP_201_CREATED)

    def create(self, data):
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def delete(self, request, user_id, format=None):
        instance = self.get_instance_or_false(
            user_id=request.user.id, following_user_id=user_id
        )
        if instance:
            detail = f" user_id: {request.user.id}, following_user_id:{user_id} is not true anymore!"
            instance.delete()
            response = Response(dict(detail=detail), status=status.HTTP_204_NO_CONTENT)
        else:
            detail = f"ObjectDoesNotExist, user_id: {request.user.id}, following_user_id:{user_id}"
            response = Response(dict(detail=detail), status=status.HTTP_404_NOT_FOUND)
        return response

    def get_instance_or_false(self, **query):
        try:
            instance = self.get_queryset().get(**query)
        except exceptions.ObjectDoesNotExist as ex:
            return False
        return instance


class UserFollowers(MixInFollowList, generics.GenericAPIView):
    queryset = UserFollow.objects.all()
    serializer_class = UserFollowSerializer
    serializer_class_user_info = UserFollowerSerializer
    pagination_class = IdCursorPagination
    filter_backends = [IsFollowersFilterBackend]

    def get(self, request, user_id, format=None):
        return_count = bool(request.query_params.get("return_count", 0))
        if return_count:
            count = self.get_queryset().filter(user_id=user_id).count()
            return Response(dict(count=count), status=status.HTTP_200_OK)
        self.follower_id = user_id
        return self.list(request)
