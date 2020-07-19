import json
from django.http import Http404, HttpResponse

from rest_framework import status, generics, mixins, filters
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from firebase_authentication import exceptions
from firebase_authentication import permissions
from wilt_til.models import Clap, Bookmark, Til, Tag
from wilt_til.serializers import TilSerializer, FeedSerializer
from wilt_til.views import IdCursorPagination

from wilt_user.models import WiltUser, UserFollow
from wilt_user.serializers import WiltUserSerializer
from wilt_user.serializers import UserFollowSerializer

from firebase_admin import auth

__all__ = (
    "UserCheck",
    "UserDetail",
    "UserTag",
    "UserClaps",
    "UserBookmark",
)


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

    def get(self, request, id, format=None):
        active_user = get_active_user_or_false(id=id)
        if active_user:
            serializer = WiltUserSerializer(active_user)
            response = Response(serializer.data, status=status.HTTP_200_OK)
        else:
            detail = "Deleted user. (is_active=False)"
            response = Response(dict(detail=detail), status=status.HTTP_204_NO_CONTENT)
        return response

    def put(self, request, id, format=None):
        user = get_user_or_false(id=id)
        if user:
            response = self.update(user, request.data, partial=False)
        else:
            response = self.get_invalid_user(id)
        return response

    def patch(self, request, id, format=None):
        user = get_user_or_false(id=id)
        if user:
            response = self.update(user, request.data, partial=True)
        else:
            response = get_invalid_user_response(id)
        return response

    def delete(self, request, id, format=None):
        user = get_user_or_false(id=id)
        if user:
            serializer = self.__update(user, dict(is_active=False), partial=True)
            detail = f"User({id}) is deleted."
            response = Response(dict(detail=detail), status=status.HTTP_204_NO_CONTENT)
        else:
            response = get_invalid_user_response(id)
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


# User가 clap한 Til 목록을 불러오는 view
class UserClaps(APIView):
    def get(self, request, id, format=None):
        active_user = get_active_user_or_false(id=id)
        if active_user:
            queryset = Clap.objects.select_related("til").filter(user=active_user)
            user_clap_list = []
            for clap in queryset:
                til = TilSerializer(clap.til)
                user_clap_list.append(til.data)
            response = Response(user_clap_list, status=status.HTTP_200_OK)
        else:
            response = get_invalid_user_response(id=id)
        return response


# User가 북마크한 Til 목록을 불러오는 view
class UserBookmark(APIView):
    def get(self, request, id, format=None):

        active_user = get_active_user_or_false(id=id)
        if active_user:
            queryset = Bookmark.objects.select_related("til").filter(user=active_user)
            user_bookmark_list = []
            for bookmark in queryset:
                til = FeedSerializer(bookmark.til)
                user_bookmark_list.append(til.data)
            response = Response(user_bookmark_list, status=status.HTTP_200_OK)
        else:
            response = get_invalid_user_response(id=id)
        return response


# User가 TIL에 사용하였던 태그들을 불러오는 view
# User의 태그 중 해당 tag가 들어간 Til 가져오는 view
class UserTag(APIView):
    def get(self, request, id, format=None):

        active_user = get_active_user_or_false(id=id)
        if active_user:
            tag_name = request.GET.get("tag_name", "")
            tils = Til.objects.filter(user=active_user).prefetch_related("tags")
            if tag_name:
                result = self.__til_info_about_tag(tils, tag_name)
            else:
                result = self.__count_tags_in_tils(tils)
            response = Response(result, status=status.HTTP_200_OK)
        else:
            response = get_invalid_user_response(id=id)
        return response

    @staticmethod
    def __count_tags_in_tils(tils):
        tags = dict()
        for til in tils:
            for tag in til.tags.all():
                if tag.name in tags.keys():
                    tags[tag.name] += 1
                else:
                    tags[tag.name] = 1
        return tags

    @staticmethod
    def __til_info_about_tag(tils, tag):
        user_til_list = []

        for til in tils:
            for tag_name in til.tags.all():
                if tag_name.name == tag:
                    user_til_list.append(TilSerializer(til).data)
                    break

        return user_til_list

# 유저의 TIL을 가져오는 view
# 페이지 네이션 적용 필
class UserTils(APIView):

    def get(self, request, id, format=None):

        result = []
        active_user = get_active_user_or_false(id=id)
        if active_user:
            user_til_list = Til.objects.filter(user=active_user)

            for til in user_til_list:
                result.append(TilSerializer(til).data)

            response = Response(result, status=status.HTTP_200_OK)
        else:
            response = get_invalid_user_response(id=id)

        return response

# 유저의 til 갯수/ 응원 갯수 / 북마크 갯수를 불러오는 view
class UserTotalCount(APIView):

    def get(self, request, id, format=None):
        result = []
        active_user = get_active_user_or_false(id=id)

        if active_user:
            # 유저의 til 갯수
            user_til_count = len(Til.objects.filter(user=active_user))

            # 유저의 응원 갯수
            user_clap_count = len(Clap.objects.filter(til__user=active_user))

            # 유저의 북마크 갯수
            user_bookmark_count = len(Bookmark.objects.filter(user=active_user))

            result['user_til_count'] = user_til_count
            result['user_clap_count'] = user_clap_count
            result['user_bookmark_count'] = user_bookmark_count

            response = Response(result, status=status.HTTP_200_OK)
        else:
            response = get_invalid_user_response(id=id)

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


class IsFollowingFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(user_id=request.user.id)


class UserFollowing(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = UserFollow.objects.all()
    serializer_class = UserFollowSerializer
    pagination_class = IdCursorPagination
    # permission_classes
    filter_backends = [IsFollowingFilterBackend]

    def get(self, request, id, format=None):
        return_count = bool(request.query_params.get("return_count", 0))
        if return_count:
            count = self.get_queryset().filter(user_id=request.user.id).count()
            return Response(dict(count=count), status=status.HTTP_200_OK)
        return self.list(request)

    def post(self, request, id, format=None):
        data = self.create(data=dict(user_id=request.user.id, following_user_id=id))
        return Response(data, status=status.HTTP_201_CREATED)

    def create(self, data):
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def delete(self, request, id, format=None):
        instance = self.get_instance_or_false(
            user_id=request.user.id, following_user_id=id
        )
        if instance:
            instance.delete()
            detail = f"{instance} is not true anymore!"
            dict(detail=detail)
            response = Response(status=status.HTTP_204_NO_CONTENT)
        else:
            detail = f"ObjectDoesNotExist, user_id: {request.user.id}, following_user_id:{id}"
            response = Response(dict(detail=detail), status=status.HTTP_404_NOT_FOUND)
        return response

    def get_instance_or_false(self, **query):
        try:
            instance = self.get_queryset().get(**query)
        except exceptions.ObjectDoesNotExist as ex:
            return False
        return instance


class IsFollowersFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(following_user_id=view.follower_id)


class UserFollowers(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = UserFollow.objects.all()
    serializer_class = UserFollowSerializer
    pagination_class = IdCursorPagination
    filter_backends = [IsFollowersFilterBackend]

    def get(self, request, id, format=None):
        return_count = bool(request.query_params.get("return_count", 0))
        if return_count:
            count = self.get_queryset().filter(user_id=id).count()
            return Response(dict(count=count), status=status.HTTP_200_OK)
        self.follower_id = id
        return self.list(request)


