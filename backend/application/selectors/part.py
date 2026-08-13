from dataclasses import dataclass

from django.db.models import QuerySet

from application.errors.part import PartNotFoundError
from application.models.part import Part


@dataclass(frozen=True, slots=True, kw_only=True)
class PartFilter:
    category: str | None = None


def get_part(*, part_id: int) -> Part:
    # スタッフ向け。未掲載も含めて取る。
    try:
        return Part.objects.get(pk=part_id)
    except Part.DoesNotExist as error:
        raise PartNotFoundError() from error


def get_listed_part(*, part_id: int) -> Part:
    # 未掲載は顧客向けには不存在。order.part_unlisted は使わない。
    try:
        return Part.objects.get(pk=part_id, is_listed=True)
    except Part.DoesNotExist as error:
        raise PartNotFoundError() from error


def list_listed_parts(*, filter: PartFilter) -> QuerySet[Part]:
    # 顧客向け。未掲載は出さない。並びは category, name。
    queryset = Part.objects.filter(is_listed=True).order_by("category", "name")
    if filter.category is not None:
        queryset = queryset.filter(category=filter.category)
    return queryset


def list_parts(*, filter: PartFilter) -> QuerySet[Part]:
    # スタッフ向け。未掲載を含む。並びは category, sku。
    queryset = Part.objects.all().order_by("category", "sku")
    if filter.category is not None:
        queryset = queryset.filter(category=filter.category)
    return queryset
