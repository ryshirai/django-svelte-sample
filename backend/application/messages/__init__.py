from application.messages.authentication import (
    AUTHENTICATION_INVALID_CREDENTIALS,
    AUTHENTICATION_REQUIRED,
    AUTHENTICATION_STAFF_REQUIRED,
    REGISTRATION_EMAIL_ALREADY_USED,
)
from application.messages.configuration import (
    CONFIGURATION_COOLER_SOCKET_MISMATCH,
    CONFIGURATION_COOLER_TOO_TALL,
    CONFIGURATION_DUPLICATE_CATEGORY,
    CONFIGURATION_FORM_FACTOR_MISMATCH,
    CONFIGURATION_GPU_TOO_LONG,
    CONFIGURATION_INCOMPLETE,
    CONFIGURATION_MEMORY_SLOT_EXCEEDED,
    CONFIGURATION_MEMORY_TYPE_MISMATCH,
    CONFIGURATION_PSU_WATTAGE_INSUFFICIENT,
    CONFIGURATION_SOCKET_MISMATCH,
    CONFIGURATION_STORAGE_INTERFACE_UNSUPPORTED,
    CONFIGURATION_UNKNOWN_CATEGORY,
)
from application.messages.input import INPUT_INVALID
from application.messages.order import (
    ORDER_INSUFFICIENT_STOCK,
    ORDER_INVALID_STATUS_TRANSITION,
    ORDER_NOT_FOUND,
    ORDER_PART_UNLISTED,
)
from application.messages.part import (
    PART_INVALID_ATTRIBUTES,
    PART_NOT_FOUND,
    PART_SKU_ALREADY_USED,
)

MESSAGES: dict[str, str] = {
    "authentication.invalid_credentials": AUTHENTICATION_INVALID_CREDENTIALS,
    "authentication.required": AUTHENTICATION_REQUIRED,
    "authentication.staff_required": AUTHENTICATION_STAFF_REQUIRED,
    "registration.email_already_used": REGISTRATION_EMAIL_ALREADY_USED,
    "input.invalid": INPUT_INVALID,
    "part.not_found": PART_NOT_FOUND,
    "part.sku_already_used": PART_SKU_ALREADY_USED,
    "part.invalid_attributes": PART_INVALID_ATTRIBUTES,
    "configuration.incomplete": CONFIGURATION_INCOMPLETE,
    "configuration.duplicate_category": CONFIGURATION_DUPLICATE_CATEGORY,
    "configuration.unknown_category": CONFIGURATION_UNKNOWN_CATEGORY,
    "configuration.socket_mismatch": CONFIGURATION_SOCKET_MISMATCH,
    "configuration.memory_type_mismatch": CONFIGURATION_MEMORY_TYPE_MISMATCH,
    "configuration.memory_slot_exceeded": CONFIGURATION_MEMORY_SLOT_EXCEEDED,
    "configuration.form_factor_mismatch": CONFIGURATION_FORM_FACTOR_MISMATCH,
    "configuration.storage_interface_unsupported": (
        CONFIGURATION_STORAGE_INTERFACE_UNSUPPORTED
    ),
    "configuration.gpu_too_long": CONFIGURATION_GPU_TOO_LONG,
    "configuration.cooler_socket_mismatch": CONFIGURATION_COOLER_SOCKET_MISMATCH,
    "configuration.cooler_too_tall": CONFIGURATION_COOLER_TOO_TALL,
    "configuration.psu_wattage_insufficient": CONFIGURATION_PSU_WATTAGE_INSUFFICIENT,
    "order.not_found": ORDER_NOT_FOUND,
    "order.part_unlisted": ORDER_PART_UNLISTED,
    "order.insufficient_stock": ORDER_INSUFFICIENT_STOCK,
    "order.invalid_status_transition": ORDER_INVALID_STATUS_TRANSITION,
}


def message_for(*, code: str) -> str:
    return MESSAGES[code]
