from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response

from wilt_policy.models import Policy
from wilt_policy.serializers import PolicySerializer


class PolicyRetrieve(APIView):
    def get(self, request, *args, **kwargs):
        policy = Policy.objects.latest("date_created")
        serializer = PolicySerializer(policy)
        return Response(serializer.data)
