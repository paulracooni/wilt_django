from django.http import Http404

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from firebase_authentication import exceptions
from firebase_authentication import permissions

from wilt_til.models import Til, Clap, Bookmark
from wilt_til.serializers import TilSerializer

from firebase_admin import auth

__all__ = ("TilListCreate", "TilRetrieveUpdateDestroy")

# Create your views here.

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

# class TilListCreate(APIView):

#     permission_classes = [permissions.IsAuthenticatedOrReadonly]

#     def get(self, request, format=None):
#         # List all Tils
#         tils = Til.objects.all()
#         serializer = TilSerializer(tils, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request, format=None):
#         # Create Til
#         print(request.data)
#         serializer = TilSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
class TilListCreate(generics.ListCreateAPIView):
    queryset = Til.objects.all()
    serializer_class = TilSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadonly]


class TilRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Til.objects.all()
    serializer_class = TilSerializer
    permission_classes = [permissions.IsAuthorUpdateOrReadOnly]
    lookup_field = "id"

    def perform_destroy(self, instance):
        serializer = self.get_serializer(
            instance, data=dict(is_active=False), partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
