import pytest

from application.errors.part import PartInvalidAttributesError, PartSkuAlreadyUsedError
from application.models.part import Part
from application.selectors.part import PartFilter, list_listed_parts
from application.services.part import UpdatePartInput, create_part, update_part
from application.tests.part_fixtures import create_compatible_parts, part_input


@pytest.mark.django_db
def test_create_part_rejects_invalid_cpu_attributes() -> None:
    with pytest.raises(PartInvalidAttributesError) as error:
        create_part(
            input=part_input(
                sku="CPU-BAD",
                name="Bad",
                category="cpu",
                socket="unknown",
                tdp_watts=65,
            )
        )
    assert error.value.details["fields"] == ["socket"]


@pytest.mark.django_db
def test_create_part_rejects_duplicate_sku() -> None:
    create_part(
        input=part_input(
            sku="CPU-AM5-A",
            name="A",
            category="cpu",
            socket="am5",
            tdp_watts=65,
        )
    )
    with pytest.raises(PartSkuAlreadyUsedError):
        create_part(
            input=part_input(
                sku="CPU-AM5-A",
                name="B",
                category="cpu",
                socket="am5",
                tdp_watts=65,
            )
        )


@pytest.mark.django_db
def test_update_part_changes_stock_and_listing() -> None:
    part_id = create_part(
        input=part_input(
            sku="CPU-AM5-A",
            name="A",
            category="cpu",
            socket="am5",
            tdp_watts=65,
        )
    )
    update_part(
        input=UpdatePartInput(part_id=part_id, stock_quantity=3, is_listed=False)
    )
    part = Part.objects.get(pk=part_id)
    assert part.stock_quantity == 3
    assert part.is_listed is False


@pytest.mark.django_db
def test_update_part_clears_unused_attributes_on_category_change() -> None:
    part_id = create_part(
        input=part_input(
            sku="CPU-AM5-A",
            name="A",
            category="cpu",
            socket="am5",
            tdp_watts=65,
        )
    )
    update_part(
        input=UpdatePartInput(
            part_id=part_id,
            category="storage",
            interface="m2",
        )
    )
    part = Part.objects.get(pk=part_id)
    assert part.category == "storage"
    assert part.interface == "m2"
    assert part.socket == ""
    assert part.tdp_watts is None


@pytest.mark.django_db
def test_list_listed_parts_excludes_unlisted() -> None:
    create_compatible_parts()
    create_part(
        input=part_input(
            sku="CPU-HIDDEN",
            name="Hidden",
            category="cpu",
            socket="am5",
            tdp_watts=65,
            is_listed=False,
        )
    )
    skus = list(list_listed_parts(filter=PartFilter()).values_list("sku", flat=True))
    assert "CPU-HIDDEN" not in skus
    assert "CPU-AM5-7600" in skus
