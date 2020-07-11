from rest_framework import serializers

from wilt_user.models import WiltUser
from wilt_til.models import Bookmark, Clap
__all__ = ("WiltUserSerializer",)

NOT_USED_WILTUSER_FIELDS = [
    "password",
    "is_superuser",
    "is_staff",
    "groups",
    "user_permissions",
]


class WiltUserSerializer(serializers.ModelSerializer):
    n_bookmark = serializers.SerializerMethodField()
    n_clap = serializers.SerializerMethodField()

    class Meta:
        model = WiltUser
        exclude = NOT_USED_WILTUSER_FIELDS

    def create(self, validated_data):
        return WiltUser.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        return WiltUser.objects.update_user(instance, **validated_data)

    def get_n_bookmark(self, obj):

        return Bookmark.objects.filter(user=obj.id).count()

    def get_n_clap(self, obj):

        return Clap.objects.filter(user=obj.id).count()