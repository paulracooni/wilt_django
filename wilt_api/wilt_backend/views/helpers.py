from django.db.models import Q

from rest_framework import filters
from rest_framework import pagination


from wilt_backend.utils import *
from wilt_backend.models import *

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

        valid_query = self.build_valid_query(
            model=queryset.model, query_params=request.query_params
        )

        if valid_query:
            queryset = queryset.filter(**valid_query)

        return queryset

    def build_valid_query(self, model, query_params):

        valid_query = dict()
        for key, val in query_params.items():
            if key == "tags":
                valid_query["tags__in"] = self.__get_tags(val)
            elif key == "content":
                valid_query["content__contains"] = val
            elif key == "title":
                valid_query["title__contains"] = val
            elif key == "job_title":
                valid_query["user__job_title"] = val
            elif key == "user__id":
                valid_query["user__id"] = val
            elif hasattr(model, key):
                valid_query[key] = val

        return valid_query

    def __get_tags(self, tags):
        instances = []
        for name in parse_tag_input(tags):
            try:
                instances.append(Tag.objects.get(name=name))
            except Tag.DoesNotExist:
                pass
        return instances


class IsFollowingFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(user_id=request.user.id)


class IsFollowersFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(following_user_id=view.follower_id)


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


def get_success_headers(data):
    try:
        return {"Location": str(data[api_settings.URL_FIELD_NAME])}
    except (TypeError, KeyError):
        return {}
