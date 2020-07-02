from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from firebase_authentication.models import User
from firebase_authentication.serializers import UserSerializer


@api_view(['POST'])
def register(request):
    """
    Create new user.
    """
    raise NotImplementedError

@api_view(['GET'])
def check_valid_display_name(request):
    """
    Create new user.
    """
    raise NotImplementedError


class Users(APIView):
    """
    List all Users, or create a new user.
    """
    def get(self, request, format=None):
        users = User.objects.all()
        print("In Users")
        print(f"request.user = {request.user}")
        print(f"request.auth = {request.auth}")
        print(f"request.is_authenticated = {request.user.is_authenticated}")
        
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    # def post(self, request, format=None):
    #     serializer = SnippetSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)