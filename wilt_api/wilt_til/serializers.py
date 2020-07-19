from rest_framework import serializers

from wilt_til.models import Til, Clap, Bookmark, Tag
from wilt_user.models import WiltUser, UserFollow
from wilt_user.serializers import WiltUserSerializer

__all__ = ("TilSerializer",)

GLOBAL_ROF = (
    "id",
    "date_created",
)


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


class FeedSerializer(TilSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = WiltUser.objects.get(id=obj.user.id)
        return MiniWiltUserSerilizer(user).data


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
            "n_following",
            "n_followers",
            "n_bookmark",
            "n_clap",
        )
        model = WiltUser


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
