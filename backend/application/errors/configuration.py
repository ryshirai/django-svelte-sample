from application.errors.base import BusinessError


class ConfigurationIncompleteError(BusinessError):
    code = "configuration.incomplete"


class ConfigurationDuplicateCategoryError(BusinessError):
    code = "configuration.duplicate_category"


class ConfigurationUnknownCategoryError(BusinessError):
    code = "configuration.unknown_category"


class ConfigurationSocketMismatchError(BusinessError):
    code = "configuration.socket_mismatch"


class ConfigurationMemoryTypeMismatchError(BusinessError):
    code = "configuration.memory_type_mismatch"


class ConfigurationMemorySlotExceededError(BusinessError):
    code = "configuration.memory_slot_exceeded"


class ConfigurationFormFactorMismatchError(BusinessError):
    code = "configuration.form_factor_mismatch"


class ConfigurationStorageInterfaceUnsupportedError(BusinessError):
    code = "configuration.storage_interface_unsupported"


class ConfigurationGpuTooLongError(BusinessError):
    code = "configuration.gpu_too_long"


class ConfigurationCoolerSocketMismatchError(BusinessError):
    code = "configuration.cooler_socket_mismatch"


class ConfigurationCoolerTooTallError(BusinessError):
    code = "configuration.cooler_too_tall"


class ConfigurationPsuWattageInsufficientError(BusinessError):
    code = "configuration.psu_wattage_insufficient"


# 決済時、Validator の先頭 issue code を typed error に写す。
CONFIGURATION_ERROR_BY_CODE: dict[str, type[BusinessError]] = {
    ConfigurationIncompleteError.code: ConfigurationIncompleteError,
    ConfigurationDuplicateCategoryError.code: ConfigurationDuplicateCategoryError,
    ConfigurationUnknownCategoryError.code: ConfigurationUnknownCategoryError,
    ConfigurationSocketMismatchError.code: ConfigurationSocketMismatchError,
    ConfigurationMemoryTypeMismatchError.code: ConfigurationMemoryTypeMismatchError,
    ConfigurationMemorySlotExceededError.code: ConfigurationMemorySlotExceededError,
    ConfigurationFormFactorMismatchError.code: ConfigurationFormFactorMismatchError,
    ConfigurationStorageInterfaceUnsupportedError.code: (
        ConfigurationStorageInterfaceUnsupportedError
    ),
    ConfigurationGpuTooLongError.code: ConfigurationGpuTooLongError,
    ConfigurationCoolerSocketMismatchError.code: ConfigurationCoolerSocketMismatchError,
    ConfigurationCoolerTooTallError.code: ConfigurationCoolerTooTallError,
    ConfigurationPsuWattageInsufficientError.code: (
        ConfigurationPsuWattageInsufficientError
    ),
}
