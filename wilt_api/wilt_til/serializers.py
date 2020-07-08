from rest_framework import serializers

from wilt_til.models import Til

__all__ = ("TilSerializer",)


class TilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Til
        fields = "__all__"
        read_only_fields = ["id", "date_created"]
