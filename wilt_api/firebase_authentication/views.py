from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

from firebase_authentication.models import User
from firebase_authentication.serializers import UserSerializer
from firebase_authentication.exceptions import UserNotFound

from firebase_authentication.permissions import IsMyself
from firebase_authentication.permissions import IsAuthenticated
from firebase_admin import auth


class UserCheck(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """
        List all user
        - This will be depreciated
        """
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        """
        Check is unused display_name
        """
        if "display_name" not in request.data.keys():
            return Response(
                dict(detail="Must include display_name in Body."),
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            User.objects.get(display_name=request.data["display_name"])
            return Response(dict(is_valid=False), status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(dict(is_valid=True), status=status.HTTP_200_OK)


class UserDetail(APIView):

    permission_classes = [IsMyself]

    def get(self, request, uid, format=None):
        """
        Return user information
        - This will be depreciated
        """
        try:
            user = User.objects.get(id=uid)
        except User.DoesNotExist:
            return Response(
                dict(detail="User doesn't exist"), status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
