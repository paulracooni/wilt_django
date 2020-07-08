from rest_framework import serializers

from wilt_til.models import Til, Clap, Bookmark

__all__ = ("TilSerializer",)

ROF = (
    "id",
    "date_created",
)


class TilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Til
        fields = "__all__"
        read_only_fields = ROF


class ClapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clap
        fields = "__all__"
        read_only_fields = ROF


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = "__all__"
        read_only_fields = ROF
