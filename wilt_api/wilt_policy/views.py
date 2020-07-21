from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response

from wilt_policy.models import *
from wilt_policy.serializers import *


class PolicyRetrieve(APIView):
    def get(self, request, *args, **kwargs):
        policy = Policy.objects.latest("date_created")
        serializer = PolicySerializer(policy)
        return Response(serializer.data)


class S3AuthInfoRetrieve(APIView):
    def get(self, request, *args, **kwargs):
        s3_auth_info = S3AuthInfo.objects.latest("date_created")
        serializer = S3AuthInfoSerializer(s3_auth_info)
        return Response(serializer.data)
