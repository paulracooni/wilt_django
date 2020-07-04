from rest_framework import serializers

from wilt_user.models import WiltUser

__all__ = ("WiltUserSerializer",)


class WiltUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = WiltUser
        fields = (
            # Firebase field
            "id",
            "display_name",
            "email",
            # Django permission field
            "is_active",
            "is_staff",
            "is_superuser",
            # Wilt field
            "company_name",
            "job_title",
            "career_year",
        )

    def create(self, validated_data):
        return WiltUser.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        return WiltUser.objects.update_user(instance, **validated_data)
