from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from application.api.serializers.configuration import (
    ConfigurationEvaluationOutputSerializer,
    EvaluateConfigurationInputSerializer,
)
from application.selectors.configuration import evaluate_pc_configuration


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def configuration_evaluate(request: Request) -> Response:
    serializer = EvaluateConfigurationInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    evaluation = evaluate_pc_configuration(
        part_ids=tuple(serializer.validated_data["part_ids"])
    )
    output = ConfigurationEvaluationOutputSerializer(
        {
            "is_valid": evaluation.is_valid,
            "issues": [
                {"code": issue.code, "details": issue.details}
                for issue in evaluation.issues
            ],
        }
    )
    return Response(output.data)
