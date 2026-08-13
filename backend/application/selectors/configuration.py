from dataclasses import dataclass

from application.errors.order import OrderPartUnlistedError
from application.errors.part import PartNotFoundError
from application.models.part import Part
from application.validators.pc_configuration import (
    ConfigurationIssue,
    ConfigurationPart,
    validate_pc_configuration,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ConfigurationEvaluation:
    is_valid: bool
    issues: tuple[ConfigurationIssue, ...]


def evaluate_pc_configuration(*, part_ids: tuple[int, ...]) -> ConfigurationEvaluation:
    # QuerySet にならない読み取りなので DTO を返す（規約 10.2 の仕様例外）。
    unique_ids = tuple(sorted(set(part_ids)))
    parts = list(Part.objects.filter(pk__in=unique_ids))
    if len(parts) != len(unique_ids):
        raise PartNotFoundError()
    # プレビューでも未掲載は part.not_found ではなく order.part_unlisted。
    for part in parts:
        if not part.is_listed:
            raise OrderPartUnlistedError(details={"sku": part.sku})
    issues = validate_pc_configuration(
        parts=tuple(_to_configuration_part(part=part) for part in parts)
    )
    return ConfigurationEvaluation(is_valid=len(issues) == 0, issues=issues)


def _to_configuration_part(*, part: Part) -> ConfigurationPart:
    return ConfigurationPart(
        category=part.category,
        socket=part.socket,
        tdp_watts=part.tdp_watts,
        memory_type=part.memory_type,
        form_factor=part.form_factor,
        memory_slot_count=part.memory_slot_count,
        sata_port_count=part.sata_port_count,
        m2_slot_count=part.m2_slot_count,
        module_count=part.module_count,
        capacity_gb=part.capacity_gb,
        length_mm=part.length_mm,
        interface=part.interface,
        wattage=part.wattage,
        max_gpu_length_mm=part.max_gpu_length_mm,
        max_cooler_height_mm=part.max_cooler_height_mm,
        height_mm=part.height_mm,
    )
