from rest_framework import serializers
from wilt_policy.models import Policy, S3AuthInfo

EXCLUDE = (
    "id",
    "date_created",
)


class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        exclude = EXCLUDE


class S3AuthInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = S3AuthInfo
        exclude = EXCLUDE
