from typing import Any

from rest_framework import serializers


class EvaluateConfigurationInputSerializer(serializers.Serializer[Any]):
    # プレビューは未完成構成も受け、incomplete を issue で返す。
    part_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=True,
    )


class ConfigurationIssueOutputSerializer(serializers.Serializer[Any]):
    code = serializers.CharField()
    details = serializers.DictField()


class ConfigurationEvaluationOutputSerializer(serializers.Serializer[Any]):
    issues = ConfigurationIssueOutputSerializer(many=True)

    def to_representation(self, instance: Any) -> dict[str, Any]:
        return {
            "is_valid": instance["is_valid"],
            "issues": ConfigurationIssueOutputSerializer(
                instance["issues"],
                many=True,
            ).data,
        }
