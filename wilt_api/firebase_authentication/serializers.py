from rest_framework import serializers

from firebase_authentication.models import User

__all__ = "UserSerializer",


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'display_name',
            'email',
            'is_active',
            'is_staff',
            'is_superuser',
        )

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
