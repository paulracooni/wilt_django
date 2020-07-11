from rest_framework import serializers

from wilt_user.models import WiltUser

__all__ = ("WiltUserSerializer",)

NOT_USED_WILTUSER_FIELDS = [
    "password",
    "is_superuser",
    "is_staff",
    "groups",
    "user_permissions",
]


class WiltUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = WiltUser
        exclude = NOT_USED_WILTUSER_FIELDS

    def create(self, validated_data):
        return WiltUser.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        return WiltUser.objects.update_user(instance, **validated_data)
