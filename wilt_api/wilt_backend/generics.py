from django.http import Http404
from django.core import exceptions

from rest_framework import status
from rest_framework import mixins
from rest_framework import generics

from rest_framework.response import Response
from rest_framework.settings import api_settings


class TilRelationAPIView(mixins.ListModelMixin, generics.GenericAPIView):
    def get(self, request, id, format=None):
        return_count = bool(request.query_params.get("return_count", 0))
        if return_count:
            count = self.get_queryset().filter(til=id).count()
            return Response(dict(count=count), status=status.HTTP_200_OK)

        self.til_id = id  # Initialize for IsTilRealtedFilterBackend
        return self.list(request)

    def post(self, request, id, format=None):
        data = self.create(til=id, user=request.user.id)
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def delete(self, request, id, format=None):
        instance = self.get_instance_or_404(til=id, user=request.user.id)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, til, user):
        serializer = self.get_serializer(data=dict(til=til, user=user))
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
