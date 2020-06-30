from django.shortcuts import render
from rest_framework.decorators import api_view
from datetime import datetime
# Create your views here.

@api_view(['GET'])
def what_time(request):
    str_time = datetime.now().strftime(r"%Y-%m-%d %H:%M:%S")
    message = f"Current server time is {str_time}"
    return Response(dict(message=message))