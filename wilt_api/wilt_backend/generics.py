from django.db.models import Q
from django.http import Http404
from django.core import exceptions

from rest_framework import status
from rest_framework import mixins
from rest_framework import generics

from rest_framework.response import Response
from rest_framework.settings import api_settings

from wilt_backend.utils import *
from wilt_backend.models import *


class MixInFollowList:
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class_user_info(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class_user_info(queryset, many=True)
        return Response(serializer.data)


class MixInTilQuery:
    def build_filter_initial(self):
        filter_initial = dict(is_active=True, is_public=True)
        if self.request.query_params.get("with_my_private", False):
            user_id = getattr(self.request.user, "id", None)
            filter_initial.update(dict(user__id=user_id))
        return filter_initial

    def build_filter_etc(self):
        filter_etc = dict()
        for key, val in self.request.query_params.items():

            if key == "tags":
                filter_etc["tags__in"] = self.__get_tags(val)
            elif key == "job_title":
                filter_etc["user__job_title"] = val
            elif hasattr(Til, key):
                filter_etc[key] = val
        return filter_etc

    @staticmethod
    def __get_tags(tags):
        instances = []
        for name in parse_tag_input(tags):
            try:
                instances.append(Tag.objects.get(name=name))
            except Tag.DoesNotExist:
                pass
        return instances

    def build_q_search(self):
        # Old way searching This code region will be depreciated
        content = self.request.query_params.get("content", False)
        if content:
            search_query = Q(content__contains=content) | Q(title__contains=content)
        # new way searching This code region will be remained
        search = self.request.query_params.get("search", False)
        if search:
            search_query = Q(content__contains=search) | Q(title__contains=search)
        else:
            search_query = Q()
        return search_query


class TilRelationAPIView(generics.GenericAPIView):
    def get(self, request, til_id, format=None):
        return_count = bool(request.query_params.get("return_count", 0))
        if return_count:
            count = self.get_queryset().filter(til=til_id).count()
            return Response(dict(count=count), status=status.HTTP_200_OK)
        self.til_id = til_id  # Initialize for IsTilRealtedFilterBackend
        return self.list(request)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class_userinfo(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class_userinfo(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, til_id, format=None):
        extra_fields = dict([(key, val) for key, val in request.data.items()])
        data = self.create(til=til_id, user=request.user.id, **extra_fields)
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def delete(self, request, til_id, format=None):
        instance = self.get_instance_or_404(til=til_id, user=request.user.id)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, til, user, **extra_fields):
        data = dict(til=til, user=user, **extra_fields)
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

    @staticmethod
    def get_success_headers(data):
        try:
            return {"Location": str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}
