from rest_framework import serializers

from wilt_user.models import WiltUser, UserFollow
from wilt_til.models import Til, Bookmark, Clap

__all__ = ("WiltUserSerializer",)

NOT_USED_WILTUSER_FIELDS = (
    "password",
    "is_superuser",
    "is_staff",
    "groups",
    "user_permissions",
)


class WiltUserSerializer(serializers.ModelSerializer):
    n_following = serializers.SerializerMethodField()
    n_followers = serializers.SerializerMethodField()
    n_bookmark = serializers.SerializerMethodField()
    n_clap = serializers.SerializerMethodField()
    n_til = serializers.SerializerMethodField()

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

    def get_n_til(self, obj):
        return Til.objects.filter(user=obj.id).count()

    def get_n_following(self, obj):
        return UserFollow.objects.filter(user_id=obj.id).count()

    def get_n_followers(self, obj):
        return UserFollow.objects.filter(following_user_id=obj.id).count()


class UserFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollow
        fields = "__all__"
