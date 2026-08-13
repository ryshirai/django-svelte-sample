from dataclasses import dataclass

from application.errors.part import PartInvalidAttributesError
from application.models.part import Part

SOCKETS = frozenset({"am5", "lga1700"})
MEMORY_TYPES = frozenset({"ddr4", "ddr5"})
FORM_FACTORS = frozenset({"atx", "m_atx", "itx"})
INTERFACES = frozenset({"sata", "m2"})

REQUIRED_STRINGS: dict[str, tuple[str, ...]] = {
    Part.Category.CPU: ("socket",),
    Part.Category.MOTHERBOARD: ("socket", "memory_type", "form_factor"),
    Part.Category.MEMORY: ("memory_type",),
    Part.Category.STORAGE: ("interface",),
    Part.Category.CASE: ("form_factor",),
    Part.Category.CPU_COOLER: ("socket",),
}

REQUIRED_INTS: dict[str, tuple[str, ...]] = {
    Part.Category.CPU: ("tdp_watts",),
    Part.Category.MOTHERBOARD: (
        "memory_slot_count",
        "sata_port_count",
        "m2_slot_count",
    ),
    Part.Category.MEMORY: ("module_count", "capacity_gb"),
    Part.Category.PSU: ("wattage",),
    Part.Category.CASE: ("max_gpu_length_mm", "max_cooler_height_mm"),
    Part.Category.GPU: ("length_mm", "tdp_watts"),
    Part.Category.CPU_COOLER: ("height_mm",),
}

ALLOWED_VALUES: dict[str, frozenset[str]] = {
    "socket": SOCKETS,
    "memory_type": MEMORY_TYPES,
    "form_factor": FORM_FACTORS,
    "interface": INTERFACES,
}

STRING_ATTRIBUTES = ("socket", "memory_type", "form_factor", "interface")
INT_ATTRIBUTES = (
    "tdp_watts",
    "memory_slot_count",
    "sata_port_count",
    "m2_slot_count",
    "module_count",
    "capacity_gb",
    "length_mm",
    "wattage",
    "max_gpu_length_mm",
    "max_cooler_height_mm",
    "height_mm",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PartAttributeValues:
    category: str
    socket: str
    tdp_watts: int | None
    memory_type: str
    form_factor: str
    memory_slot_count: int | None
    sata_port_count: int | None
    m2_slot_count: int | None
    module_count: int | None
    capacity_gb: int | None
    length_mm: int | None
    interface: str
    wattage: int | None
    max_gpu_length_mm: int | None
    max_cooler_height_mm: int | None
    height_mm: int | None


def validate_part_attributes(*, values: PartAttributeValues) -> None:
    # 使わない属性は空文字 / NULL でよい。必須と、空でない選択値だけ見る。
    if values.category not in Part.Category.values:
        raise PartInvalidAttributesError(details={"fields": ["category"]})
    fields = [
        *_missing_strings(values=values),
        *_missing_ints(values=values),
        *_invalid_choices(values=values),
        *_unused_populated(values=values),
    ]
    if fields:
        raise PartInvalidAttributesError(details={"fields": fields})


def unused_attribute_defaults(*, category: str) -> dict[str, str | None]:
    used = set(REQUIRED_STRINGS.get(category, ())) | set(
        REQUIRED_INTS.get(category, ())
    )
    defaults: dict[str, str | None] = {}
    for field_name in STRING_ATTRIBUTES:
        if field_name not in used:
            defaults[field_name] = ""
    for field_name in INT_ATTRIBUTES:
        if field_name not in used:
            defaults[field_name] = None
    return defaults


def _missing_strings(*, values: PartAttributeValues) -> list[str]:
    missing: list[str] = []
    for field_name in REQUIRED_STRINGS.get(values.category, ()):
        if getattr(values, field_name) == "":
            missing.append(field_name)
    return missing


def _missing_ints(*, values: PartAttributeValues) -> list[str]:
    missing: list[str] = []
    for field_name in REQUIRED_INTS.get(values.category, ()):
        if getattr(values, field_name) is None:
            missing.append(field_name)
    return missing


def _invalid_choices(*, values: PartAttributeValues) -> list[str]:
    invalid: list[str] = []
    for field_name, allowed in ALLOWED_VALUES.items():
        current = getattr(values, field_name)
        if current != "" and current not in allowed:
            invalid.append(field_name)
    return invalid


def _unused_populated(*, values: PartAttributeValues) -> list[str]:
    unused: list[str] = []
    for field_name, empty in unused_attribute_defaults(
        category=values.category
    ).items():
        if getattr(values, field_name) != empty:
            unused.append(field_name)
    return unused
