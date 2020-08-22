from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from wilt_policy.models import *
from wilt_policy.serializers import *
from wilt_backend.permissions import *

class PolicyRetrieve(APIView):
    def get(self, request, *args, **kwargs):
        policy = Policy.objects.latest("date_created")
        serializer = PolicySerializer(policy)
        return Response(serializer.data)


class S3AuthInfoRetrieve(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        s3_auth_info = S3AuthInfo.objects.latest("date_created")
        serializer = S3AuthInfoSerializer(s3_auth_info)
        return Response(serializer.data)


def tos_view(request):
    policy = Policy.objects.latest("date_created")
    data = dict(
        terms_of_service=policy.terms_of_service,
        privacy_statement=policy.privacy_statement,
    )
    return render(request, "policy.html", data)


# class Policy_Web(APIView):
#     permission_classes = [permissions.AllowAny]
#     # renderer_classes = [TemplateHTMLRenderer]
#     # template_name = 'policy.html'

#     def get(self, request, *args, **kwargs):
#         policy = Policy.objects.latest("date_created")
#         return HttpResponse('<h1>Page was found</h1>')
