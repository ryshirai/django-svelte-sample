from application.errors.base import BusinessError


class PartNotFoundError(BusinessError):
    code = "part.not_found"
    http_status = 404


class PartSkuAlreadyUsedError(BusinessError):
    code = "part.sku_already_used"


class PartInvalidAttributesError(BusinessError):
    code = "part.invalid_attributes"
