from typing import Any

from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from application.errors.base import BusinessError
from application.messages import message_for


def application_exception_handler(
    exc: Exception,
    context: dict[str, Any],
) -> Response | None:
    if isinstance(exc, BusinessError):
        return _error_response(
            code=exc.code,
            http_status=exc.http_status,
            details=exc.details,
        )
    if isinstance(exc, NotAuthenticated):
        return _error_response(
            code="authentication.required",
            http_status=status.HTTP_401_UNAUTHORIZED,
            details={},
        )
    if isinstance(exc, PermissionDenied):
        # CSRF 失敗も PermissionDenied になる。スタッフ拒否と混ぜない。
        if "CSRF" in str(exc.detail):
            return _error_response(
                code="input.invalid",
                http_status=status.HTTP_403_FORBIDDEN,
                details={},
            )
        # 顧客が staff API に来た 403。authentication.required は使わない。
        return _error_response(
            code="authentication.staff_required",
            http_status=status.HTTP_403_FORBIDDEN,
            details={},
        )
    if isinstance(exc, ValidationError):
        return _error_response(
            code="input.invalid",
            http_status=status.HTTP_400_BAD_REQUEST,
            details=_validation_details(exc=exc),
        )
    if isinstance(exc, APIException):
        # 未定義 code は足さない。framework 例外は input.invalid の envelope。
        return _error_response(
            code="input.invalid",
            http_status=int(exc.status_code),
            details={},
        )
    return drf_exception_handler(exc, context)


def _error_response(
    *,
    code: str,
    http_status: int,
    details: dict[str, object],
) -> Response:
    return Response(
        {
            "error": {
                "code": code,
                "message": message_for(code=code),
                "details": details,
            }
        },
        status=http_status,
    )


def _validation_details(*, exc: ValidationError) -> dict[str, object]:
    if isinstance(exc.detail, dict):
        return {str(key): value for key, value in exc.detail.items()}
    return {"non_field_errors": exc.detail}
