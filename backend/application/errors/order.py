from application.errors.base import BusinessError


class OrderNotFoundError(BusinessError):
    # 不存在と他人の注文を同じ code にする。
    code = "order.not_found"
    http_status = 404


class OrderPartUnlistedError(BusinessError):
    code = "order.part_unlisted"


class OrderInsufficientStockError(BusinessError):
    code = "order.insufficient_stock"


class OrderInvalidStatusTransitionError(BusinessError):
    code = "order.invalid_status_transition"
