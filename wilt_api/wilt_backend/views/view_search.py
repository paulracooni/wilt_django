from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import status, mixins, generics, pagination

from wilt_backend.utils import *
from wilt_backend.models import *
from wilt_backend.generics import *
from wilt_backend.permissions import *
from wilt_backend.serializers import *
from wilt_backend.views.helpers import *
from wilt_backend.views.view_tils import attach_did_something
from functools import reduce


class SearchTils(APIView):
    permission_classes = [permissions.IsAuthenticated]
    possible_params = (
        "tags",
        "context",
        "title",
        "content",
    )

    def get(self, request, format=None):
        is_valid_params, invalid_params = self.check_params()
        if is_valid_params:
            # Query data
            query = self.__build_q_all()
            queryset = Til.objects.filter(query)

            # Pagenation
            paginator = IdCursorPagination()
            queryset = paginator.paginate_queryset(queryset, self.request, view=self)
            serializer = FeedSerializer(queryset, many=True)

            # Attach additional info (it can't be attached by serializer)
            response_data = attach_did_something(
                data=serializer.data, user_id=getattr(request.user, "id", None)
            )

            # Response data
            response = paginator.get_paginated_response(response_data)
        else:
            detail = dict(
                detail="Bad requst of /search/tils.",
                invalid_params=invalid_params,
                possible_params=self.possible_params,
            )
            response = Response(detail, status=status.HTTP_400_BAD_REQUEST)

        return response

    def check_params(self):
        params = self.request.query_params
        is_params = bool(len(params))
        invalid_params = list(set(params.keys()) - set(self.possible_params))
        is_invalid_params = bool(invalid_params)
        return is_params and not is_invalid_params, invalid_params

    def __build_q_all(self):
        # Due to params checked before calling search,
        # param only can be one of possible_params.
        list_qs = [Q(is_active=True), Q(is_public=True)]
        for key, val in self.request.query_params.items():
            if key == "tags":
                list_qs.append(self.__build_q_tags_and_save_log(val))
            elif key == "context":
                list_qs.append(self.__build_q_context_and_save_log(val))
            elif key == "title":
                list_qs.append(self.__build_q_title_and_save_log(val))
            elif key == "content":
                list_qs.append(self.__build_q_content_and_save_log(val))

        query = reduce(lambda q1, q2: q1 & q2, list_qs)
        return query

    def __build_q_tags_and_save_log(self, tags):
        tags = self.__get_tags(tags)
        for tag in tags:
            self.__save_log(search_type="tag", keyword=tag.name)
        return Q(tags__in=tags)

    def __build_q_context_and_save_log(self, context):
        self.__save_log(search_type="context", keyword=context)
        return Q(content__contains=context) | Q(title__contains=context)

    def __build_q_title_and_save_log(self, title):
        self.__save_log(search_type="title", keyword=title)
        return Q(title__contains=title)

    def __build_q_content_and_save_log(self, content):
        self.__save_log(search_type="content", keyword=content)
        return Q(content__contains=content)

    def __save_log(self, search_type, keyword):
        log_data = dict(
            user=self.request.user.id,
            search_entity="til",
            search_type=search_type,
            keyword=keyword,
        )

        serializer = LogSearchSerializer(data=log_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def __get_tags(self, tags):
        instances = []
        for name in parse_tag_input(tags):
            try:
                instances.append(Tag.objects.get(name=name))
            except Tag.DoesNotExist:
                pass
        return instances


class HotTagRetrive(APIView):
    def get(self, request, format=None):
        queryset = LogSearch.objects.all()
        for q in queryset:
            print(q)
        return Response(status=status.HTTP_200_OK)


# class SearchUsers(APIView):

#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, format=None):

#         raise NotImplementedError
