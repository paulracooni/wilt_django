from rest_framework import serializers

from wilt_til.models import Til, Clap, Bookmark, Tag

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
    tags = serializers.SlugRelatedField(
        many=True, queryset=Tag.objects.all(), slug_field="name"
    )

    class Meta:
        model = Til
        fields = "__all__"
        read_only_fields = GLOBAL_ROF


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
