from application.errors.base import BusinessError


class InputInvalidError(BusinessError):
    code = "input.invalid"
