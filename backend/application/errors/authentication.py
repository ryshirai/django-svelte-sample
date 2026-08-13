from application.errors.base import BusinessError


class AuthenticationInvalidCredentialsError(BusinessError):
    code = "authentication.invalid_credentials"
    http_status = 401


class AuthenticationRequiredError(BusinessError):
    code = "authentication.required"
    http_status = 401


class AuthenticationStaffRequiredError(BusinessError):
    code = "authentication.staff_required"
    http_status = 403


class RegistrationEmailAlreadyUsedError(BusinessError):
    code = "registration.email_already_used"
