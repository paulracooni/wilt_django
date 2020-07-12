import json
from django.http import Http404, HttpResponse

from rest_framework import status, generics, mixins, filters
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from firebase_authentication import exceptions
from firebase_authentication import permissions
from wilt_til.models import Clap, Bookmark, Til, Tag
from wilt_til.serializers import TilSerializer
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

# class UserDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = WiltUser.objects.all()
#     serializer_class = WiltUserSerializer
#     permission_classes = [permissions.IsMyself]
#     lookup_field  = "id"

#     def partial_update(self, request, *args, **kwargs):
#         kwargs['partial'] = True
#         return self.update(request, *args, **kwargs)

#     def perform_destroy(self, instance):
#         serializer = self.get_serializer(
#             instance, data=dict(is_active=False), partial=True)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)


def get_user_or_404(id):
    try:
        user = WiltUser.objects.get(id=id)
    except WiltUser.DoesNotExist as ex:
        raise Http404
    return user


def get_active_user_or_404(id):
    user = get_user_or_404(id)
    if not user.is_active:
        raise Http404
    return user


class UserDetail(APIView):

    permission_classes = [permissions.IsMyself]
    NO_UPDATE_FIELD = ("id", "email", "is_staff", "is_superuser")

    def get(self, request, id, format=None):
        user = get_active_user_or_404(id=id)
        serializer = WiltUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id, format=None):
        user = get_user_or_404(id=id)
        fields = self.__filter_fields(request.data)
        serializer = self.__update(user, fields, partial=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id, format=None):
        user = get_user_or_404(id=id)
        fields = self.__filter_fields(request.data)
        serializer = self.__update(user, fields, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id, format=None):
        user = get_user_or_404(id=id)
        serializer = self.__update(user, dict(is_active=False), partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        user = get_active_user_or_404(id=id)
        queryset = Clap.objects.select_related("til").filter(user=user)
        user_clap_list = []

        for clap in queryset:
            til = TilSerializer(clap.til)
            user_clap_list.append(til.data)

        return Response(user_clap_list, status=status.HTTP_200_OK)


# User가 북마크한 Til 목록을 불러오는 view
class UserBookmark(APIView):
    def get(self, request, id, format=None):
        user = get_active_user_or_404(id=id)
        queryset = Bookmark.objects.select_related("til").filter(user=user)
        user_bookmark_list = []

        for bookmark in queryset:
            til = TilSerializer(bookmark.til)
            user_bookmark_list.append(til.data)

        return Response(user_bookmark_list, status=status.HTTP_200_OK)


# User가 TIL에 사용하였던 태그들을 불러오는 view
# User의 태그 중 해당 tag가 들어간 Til 가져오는 view
class UserTag(APIView):
    def get(self, request, id, format=None):
        user = get_active_user_or_404(id=id)
        tag_name = request.GET.get("tag_name", "")
        tils = Til.objects.filter(user=user).prefetch_related("tags")

        if tag_name:
            result = self.__til_info_about_tag(tils, tag_name)

        else:
            result = self.__count_tags_in_tils(tils)

        return Response(result, status=status.HTTP_200_OK)

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

    def delete(self, request, id, format=None):
        instance = self.get_instance_or_404(
            user_id=request.user.id, following_user_id=id
        )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, data):
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def get_instance_or_404(self, **query):
        try:
            instance = self.get_queryset().get(**query)
        except exceptions.ObjectDoesNotExist as ex:
            raise Http404
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
