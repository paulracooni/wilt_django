from rest_framework import serializers
from wilt_backend.models import WiltUser, UserFollow, Til, Bookmark, Clap, Tag

# All serializers defined as bellow
__all__ = (
    "WiltUserSerializer",
    "UserFollowSerializer",
    "TagSerializer",
    "TilSerializer",
    "FeedSerializer",
    "MiniWiltUserSerilizer",
    "ClapSerializer",
    "ClapUserInfoSerializer",
    "BookmarkSerializer",
    "BookmarkUserInfoSerializer",
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


class MiniWiltUserSerilizer(WiltUserSerializer):
    class Meta:
        fields = (
            "id",
            "display_name",
            "picture",
            "description",
            "company_name",
            "job_title",
            "career_year",
        )
        model = WiltUser


class MixInUserInfo:
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = WiltUser.objects.get(id=obj.user.id)
        return MiniWiltUserSerilizer(user).data


class UserFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollow
        fields = "__all__"


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
    class Meta:
        model = Clap
        fields = "__all__"
        read_only_fields = GLOBAL_ROF


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = "__all__"
        read_only_fields = GLOBAL_ROF


class FeedSerializer(MixInUserInfo, TilSerializer):
    pass


class ClapUserInfoSerializer(MixInUserInfo, ClapSerializer):
    pass


class BookmarkUserInfoSerializer(MixInUserInfo, BookmarkSerializer):
    pass
