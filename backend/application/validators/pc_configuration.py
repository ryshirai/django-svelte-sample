from dataclasses import dataclass

from application.models.part import Part

REQUIRED_CATEGORIES = (
    Part.Category.CPU,
    Part.Category.MOTHERBOARD,
    Part.Category.MEMORY,
    Part.Category.STORAGE,
    Part.Category.PSU,
    Part.Category.CASE,
)
KNOWN_CATEGORIES = frozenset(Part.Category.values)
# 必要ワット = CPU TDP + GPU TDP + この余り。GPU なしの TDP は 0。
PSU_HEADROOM_WATTS = 100


@dataclass(frozen=True, slots=True, kw_only=True)
class ConfigurationPart:
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


@dataclass(frozen=True, slots=True, kw_only=True)
class ConfigurationIssue:
    code: str
    details: dict[str, object]


def validate_pc_configuration(
    *,
    parts: tuple[ConfigurationPart, ...],
) -> tuple[ConfigurationIssue, ...]:
    issues = [
        *_category_issues(parts=parts),
        *_socket_issues(parts=parts),
        *_memory_issues(parts=parts),
        *_form_factor_issues(parts=parts),
        *_storage_issues(parts=parts),
        *_gpu_issues(parts=parts),
        *_cooler_issues(parts=parts),
        *_psu_issues(parts=parts),
    ]
    return tuple(issues)


def _by_category(
    *,
    parts: tuple[ConfigurationPart, ...],
) -> dict[str, list[ConfigurationPart]]:
    grouped: dict[str, list[ConfigurationPart]] = {}
    for part in parts:
        grouped.setdefault(part.category, []).append(part)
    return grouped


def _one(
    *,
    grouped: dict[str, list[ConfigurationPart]],
    category: str,
) -> ConfigurationPart | None:
    items = grouped.get(category, [])
    # 欠落・重複はカテゴリ issue 側。ペア比較はちょうど 1 個のときだけ。
    if len(items) != 1:
        return None
    return items[0]


def _category_issues(
    *,
    parts: tuple[ConfigurationPart, ...],
) -> list[ConfigurationIssue]:
    grouped = _by_category(parts=parts)
    issues: list[ConfigurationIssue] = []
    unknown = sorted(
        category for category in grouped if category not in KNOWN_CATEGORIES
    )
    for category in unknown:
        issues.append(
            ConfigurationIssue(
                code="configuration.unknown_category",
                details={"category": category},
            )
        )
    duplicates = sorted(
        category
        for category, items in grouped.items()
        if category in KNOWN_CATEGORIES and len(items) > 1
    )
    for category in duplicates:
        issues.append(
            ConfigurationIssue(
                code="configuration.duplicate_category",
                details={"category": category},
            )
        )
    missing = [category for category in REQUIRED_CATEGORIES if category not in grouped]
    if missing:
        issues.append(
            ConfigurationIssue(
                code="configuration.incomplete",
                details={"missing_categories": missing},
            )
        )
    return issues


def _socket_issues(
    *,
    parts: tuple[ConfigurationPart, ...],
) -> list[ConfigurationIssue]:
    grouped = _by_category(parts=parts)
    cpu = _one(grouped=grouped, category=Part.Category.CPU)
    motherboard = _one(grouped=grouped, category=Part.Category.MOTHERBOARD)
    if cpu is None or motherboard is None:
        return []
    if cpu.socket == motherboard.socket:
        return []
    return [
        ConfigurationIssue(
            code="configuration.socket_mismatch",
            details={
                "cpu_socket": cpu.socket,
                "motherboard_socket": motherboard.socket,
            },
        )
    ]


def _memory_issues(
    *,
    parts: tuple[ConfigurationPart, ...],
) -> list[ConfigurationIssue]:
    grouped = _by_category(parts=parts)
    memory = _one(grouped=grouped, category=Part.Category.MEMORY)
    motherboard = _one(grouped=grouped, category=Part.Category.MOTHERBOARD)
    if memory is None or motherboard is None:
        return []
    issues: list[ConfigurationIssue] = []
    if memory.memory_type != motherboard.memory_type:
        issues.append(
            ConfigurationIssue(
                code="configuration.memory_type_mismatch",
                details={
                    "memory_type": memory.memory_type,
                    "motherboard_memory_type": motherboard.memory_type,
                },
            )
        )
    if (
        memory.module_count is not None
        and motherboard.memory_slot_count is not None
        and memory.module_count > motherboard.memory_slot_count
    ):
        issues.append(
            ConfigurationIssue(
                code="configuration.memory_slot_exceeded",
                details={
                    "module_count": memory.module_count,
                    "memory_slot_count": motherboard.memory_slot_count,
                },
            )
        )
    return issues


def _form_factor_issues(
    *,
    parts: tuple[ConfigurationPart, ...],
) -> list[ConfigurationIssue]:
    grouped = _by_category(parts=parts)
    case = _one(grouped=grouped, category=Part.Category.CASE)
    motherboard = _one(grouped=grouped, category=Part.Category.MOTHERBOARD)
    if case is None or motherboard is None:
        return []
    # 包含関係は見ない。ケースと MB の form_factor が一致すること。
    if case.form_factor == motherboard.form_factor:
        return []
    return [
        ConfigurationIssue(
            code="configuration.form_factor_mismatch",
            details={
                "case_form_factor": case.form_factor,
                "motherboard_form_factor": motherboard.form_factor,
            },
        )
    ]


def _storage_issues(
    *,
    parts: tuple[ConfigurationPart, ...],
) -> list[ConfigurationIssue]:
    grouped = _by_category(parts=parts)
    storage = _one(grouped=grouped, category=Part.Category.STORAGE)
    motherboard = _one(grouped=grouped, category=Part.Category.MOTHERBOARD)
    if storage is None or motherboard is None:
        return []
    if storage.interface == "m2" and (motherboard.m2_slot_count or 0) >= 1:
        return []
    if storage.interface == "sata" and (motherboard.sata_port_count or 0) >= 1:
        return []
    return [
        ConfigurationIssue(
            code="configuration.storage_interface_unsupported",
            details={"interface": storage.interface},
        )
    ]


def _gpu_issues(
    *,
    parts: tuple[ConfigurationPart, ...],
) -> list[ConfigurationIssue]:
    grouped = _by_category(parts=parts)
    gpu = _one(grouped=grouped, category=Part.Category.GPU)
    case = _one(grouped=grouped, category=Part.Category.CASE)
    if gpu is None or case is None:
        return []
    if (
        gpu.length_mm is None
        or case.max_gpu_length_mm is None
        or gpu.length_mm <= case.max_gpu_length_mm
    ):
        return []
    return [
        ConfigurationIssue(
            code="configuration.gpu_too_long",
            details={
                "gpu_length_mm": gpu.length_mm,
                "max_gpu_length_mm": case.max_gpu_length_mm,
            },
        )
    ]


def _cooler_issues(
    *,
    parts: tuple[ConfigurationPart, ...],
) -> list[ConfigurationIssue]:
    grouped = _by_category(parts=parts)
    cooler = _one(grouped=grouped, category=Part.Category.CPU_COOLER)
    cpu = _one(grouped=grouped, category=Part.Category.CPU)
    case = _one(grouped=grouped, category=Part.Category.CASE)
    if cooler is None:
        return []
    issues: list[ConfigurationIssue] = []
    if cpu is not None and cooler.socket != cpu.socket:
        issues.append(
            ConfigurationIssue(
                code="configuration.cooler_socket_mismatch",
                details={
                    "cooler_socket": cooler.socket,
                    "cpu_socket": cpu.socket,
                },
            )
        )
    if (
        case is not None
        and cooler.height_mm is not None
        and case.max_cooler_height_mm is not None
        and cooler.height_mm > case.max_cooler_height_mm
    ):
        issues.append(
            ConfigurationIssue(
                code="configuration.cooler_too_tall",
                details={
                    "cooler_height_mm": cooler.height_mm,
                    "max_cooler_height_mm": case.max_cooler_height_mm,
                },
            )
        )
    return issues


def _psu_issues(
    *,
    parts: tuple[ConfigurationPart, ...],
) -> list[ConfigurationIssue]:
    grouped = _by_category(parts=parts)
    psu = _one(grouped=grouped, category=Part.Category.PSU)
    cpu = _one(grouped=grouped, category=Part.Category.CPU)
    if psu is None or cpu is None or psu.wattage is None:
        return []
    gpu = _one(grouped=grouped, category=Part.Category.GPU)
    gpu_tdp = gpu.tdp_watts if gpu is not None and gpu.tdp_watts is not None else 0
    cpu_tdp = cpu.tdp_watts or 0
    required = cpu_tdp + gpu_tdp + PSU_HEADROOM_WATTS
    if psu.wattage >= required:
        return []
    return [
        ConfigurationIssue(
            code="configuration.psu_wattage_insufficient",
            details={
                "required_wattage": required,
                "psu_wattage": psu.wattage,
            },
        )
    ]
