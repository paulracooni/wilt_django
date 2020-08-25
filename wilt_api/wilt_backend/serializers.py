from rest_framework import serializers
from wilt_backend.models import *

# All serializers defined as bellow
from wilt_backend.models import Plant

__all__ = (
    "WiltUserSerializer",
    "TagSerializer",
    "TilSerializer",
    "FeedSerializer",
    "MiniWiltUserSerilizer",
    "ClapSerializer",
    "ClapUserInfoSerializer",
    "BookmarkSerializer",
    "BookmarkUserInfoSerializer",
    "CommentSerializer",
    "CommentUserInfoSerializer",
    "UserFollowSerializer",
    "UserFollowerSerializer",
    "UserFollowingSerializer",
    "LogSearchSerializer",
)

# Global read only field
GLOBAL_ROF = (
    "id",
    "date_created",
)

NOT_USED_WILTUSER_FIELDS = (
    "password",
    "is_superuser",
    "is_staff",
    "groups",
    "user_permissions",
)

valid_relation = dict(til__is_active=True, til__is_public=True)


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

        return Bookmark.objects.filter(user=obj.id, **valid_relation).count()

    def get_n_clap(self, obj):
        return Clap.objects.filter(til__user=obj.id, **valid_relation).count()

    def get_n_til(self, obj):
        return Til.objects.filter(user=obj.id, is_active=True).count()

    def get_n_following(self, obj):
        return UserFollow.objects.filter(user_id=obj.id).count()

    def get_n_followers(self, obj):
        return UserFollow.objects.filter(following_user_id=obj.id).count()


class MiniWiltUserSerilizer(WiltUserSerializer):
    class Meta:
        fields = (
            "id",
            "email",
            "display_name",
            "picture",
            "description",
            "company_name",
            "job_title",
            "career_year",
            "n_clap",
            "n_bookmark",
            "n_til",
        )
        model = WiltUser


class TagSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="id")

    class Meta:
        model = Tag


class TilSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True)
    is_public = serializers.BooleanField(default=True)
    n_bookmark = serializers.SerializerMethodField()
    n_clap = serializers.SerializerMethodField()
    tags = serializers.SlugRelatedField(
        many=True, queryset=Tag.objects.all(), slug_field="name"
    )

    class Meta:
        model = Til
        fields = "__all__"
        read_only_fields = GLOBAL_ROF + ("n_bookmark", "n_clap",)

    def get_n_bookmark(self, obj):

        return Bookmark.objects.filter(til=obj).count()

    def get_n_clap(self, obj):

        return Clap.objects.filter(til=obj).count()


class ClapSerializer(serializers.ModelSerializer):
    til_name = serializers.SerializerMethodField()

    class Meta:
        model = Clap
        fields = "__all__"
        read_only_fields = GLOBAL_ROF

    def get_til_name(self, obj):
        clap = Clap.objects.select_related("til").get(id=obj.id)

        return clap.til.title


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = "__all__"
        read_only_fields = GLOBAL_ROF


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = GLOBAL_ROF

class PlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plant
        fields = (
            "id",
            "plant_id",
            "plant_name",
            "til_count",
            "satellite",
            "date_created",
            "completed_date",
        )


class FeedSerializer(TilSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = WiltUser.objects.get(id=obj.user.id)
        return MiniWiltUserSerilizer(user).data


class ClapUserInfoSerializer(ClapSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = WiltUser.objects.get(id=obj.user.id)
        return MiniWiltUserSerilizer(user).data


class BookmarkUserInfoSerializer(BookmarkSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = WiltUser.objects.get(id=obj.user.id)
        return MiniWiltUserSerilizer(user).data


class CommentUserInfoSerializer(CommentSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = WiltUser.objects.get(id=obj.user.id)
        return MiniWiltUserSerilizer(user).data


class UserFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollow
        fields = "__all__"


class UserFollowerSerializer(serializers.ModelSerializer):
    """
    나를 팔로우 한 유저
    """

    user = serializers.SerializerMethodField()

    class Meta:
        model = UserFollow
        fields = "__all__"

    def get_user(self, obj):
        user = WiltUser.objects.get(id=obj.user_id.id)
        return MiniWiltUserSerilizer(user).data


class UserFollowingSerializer(serializers.ModelSerializer):
    """
    내가 팔로우 하고 있는 유저
    """

    user = serializers.SerializerMethodField()

    class Meta:
        model = UserFollow
        fields = "__all__"

    def get_user(self, obj):
        user = WiltUser.objects.get(id=obj.following_user_id.id)
        return MiniWiltUserSerilizer(user).data


class LogSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogSearch
        fields = "__all__"

    # def create(self, validated_data):
    #     return self.Meta.model(**validated_data)
