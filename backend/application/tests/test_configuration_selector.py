import pytest

from application.errors.order import OrderPartUnlistedError
from application.errors.part import PartNotFoundError
from application.selectors.configuration import evaluate_pc_configuration
from application.services.part import create_part
from application.tests.part_fixtures import create_compatible_parts, part_input


@pytest.mark.django_db
def test_evaluate_pc_configuration_returns_socket_mismatch_issue() -> None:
    parts = create_compatible_parts()
    bad_cpu = create_part(
        input=part_input(
            sku="CPU-1700",
            name="Intel",
            category="cpu",
            socket="lga1700",
            tdp_watts=65,
        )
    )
    evaluation = evaluate_pc_configuration(
        part_ids=(
            bad_cpu,
            parts["motherboard"].id,
            parts["memory"].id,
            parts["storage"].id,
            parts["psu"].id,
            parts["case"].id,
        )
    )
    assert evaluation.is_valid is False
    assert evaluation.issues[0].code == "configuration.socket_mismatch"


@pytest.mark.django_db
def test_evaluate_pc_configuration_accepts_compatible_build() -> None:
    parts = create_compatible_parts()
    evaluation = evaluate_pc_configuration(
        part_ids=(
            parts["cpu"].id,
            parts["motherboard"].id,
            parts["memory"].id,
            parts["storage"].id,
            parts["psu"].id,
            parts["case"].id,
            parts["gpu"].id,
            parts["cpu_cooler"].id,
        )
    )
    assert evaluation.is_valid is True
    assert evaluation.issues == ()


@pytest.mark.django_db
def test_evaluate_pc_configuration_rejects_unlisted_part() -> None:
    parts = create_compatible_parts()
    parts["cpu"].is_listed = False
    parts["cpu"].save(update_fields=["is_listed"])
    with pytest.raises(OrderPartUnlistedError):
        evaluate_pc_configuration(
            part_ids=(
                parts["cpu"].id,
                parts["motherboard"].id,
                parts["memory"].id,
                parts["storage"].id,
                parts["psu"].id,
                parts["case"].id,
            )
        )


@pytest.mark.django_db
def test_evaluate_pc_configuration_rejects_missing_part() -> None:
    with pytest.raises(PartNotFoundError):
        evaluate_pc_configuration(part_ids=(999_999,))
