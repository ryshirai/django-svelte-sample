from decimal import Decimal

from application.models.part import Part
from application.services.part import CreatePartInput, create_part


def create_compatible_parts() -> dict[str, Part]:
    ids = {
        "cpu": _cpu(sku="CPU-AM5-7600", socket="am5"),
        "motherboard": _motherboard(),
        "memory": _memory(memory_type="ddr5"),
        "storage": _storage(),
        "psu": _psu(wattage=650),
        "case": _case(
            form_factor="atx",
            max_gpu_length_mm=360,
            max_cooler_height_mm=160,
        ),
        "gpu": _gpu(length_mm=304, tdp_watts=200),
        "cpu_cooler": _cooler(socket="am5", height_mm=155),
    }
    return {key: Part.objects.get(pk=part_id) for key, part_id in ids.items()}


def compatible_part_ids(*, extras: bool = False) -> list[int]:
    parts = create_compatible_parts()
    ids = [
        parts["cpu"].id,
        parts["motherboard"].id,
        parts["memory"].id,
        parts["storage"].id,
        parts["psu"].id,
        parts["case"].id,
    ]
    if extras:
        ids.extend([parts["gpu"].id, parts["cpu_cooler"].id])
    return ids


def _cpu(*, sku: str, socket: str, is_listed: bool = True, stock: int = 10) -> int:
    return create_part(
        input=part_input(
            sku=sku,
            name=sku,
            category="cpu",
            socket=socket,
            tdp_watts=65,
            is_listed=is_listed,
            stock_quantity=stock,
        )
    )


def _motherboard() -> int:
    return create_part(
        input=part_input(
            sku="MB-AM5-ATX",
            name="MB",
            category="motherboard",
            socket="am5",
            memory_type="ddr5",
            form_factor="atx",
            memory_slot_count=4,
            sata_port_count=4,
            m2_slot_count=2,
        )
    )


def _memory(*, memory_type: str) -> int:
    return create_part(
        input=part_input(
            sku=f"MEM-{memory_type.upper()}",
            name="MEM",
            category="memory",
            memory_type=memory_type,
            module_count=2,
            capacity_gb=32,
        )
    )


def _storage() -> int:
    return create_part(
        input=part_input(
            sku="SSD-M2-1T",
            name="SSD",
            category="storage",
            interface="m2",
        )
    )


def _psu(*, wattage: int) -> int:
    return create_part(
        input=part_input(
            sku=f"PSU-{wattage}",
            name="PSU",
            category="psu",
            wattage=wattage,
        )
    )


def _case(
    *,
    form_factor: str,
    max_gpu_length_mm: int,
    max_cooler_height_mm: int,
) -> int:
    return create_part(
        input=part_input(
            sku=f"CASE-{form_factor.upper()}",
            name="CASE",
            category="case",
            form_factor=form_factor,
            max_gpu_length_mm=max_gpu_length_mm,
            max_cooler_height_mm=max_cooler_height_mm,
        )
    )


def _gpu(*, length_mm: int, tdp_watts: int) -> int:
    return create_part(
        input=part_input(
            sku="GPU-4070",
            name="GPU",
            category="gpu",
            length_mm=length_mm,
            tdp_watts=tdp_watts,
        )
    )


def _cooler(*, socket: str, height_mm: int) -> int:
    return create_part(
        input=part_input(
            sku="CLR-AM5",
            name="CLR",
            category="cpu_cooler",
            socket=socket,
            height_mm=height_mm,
        )
    )


def part_input(
    *,
    sku: str,
    name: str,
    category: str,
    unit_price: str = "1000",
    stock_quantity: int = 10,
    is_listed: bool = True,
    socket: str = "",
    tdp_watts: int | None = None,
    memory_type: str = "",
    form_factor: str = "",
    memory_slot_count: int | None = None,
    sata_port_count: int | None = None,
    m2_slot_count: int | None = None,
    module_count: int | None = None,
    capacity_gb: int | None = None,
    length_mm: int | None = None,
    interface: str = "",
    wattage: int | None = None,
    max_gpu_length_mm: int | None = None,
    max_cooler_height_mm: int | None = None,
    height_mm: int | None = None,
) -> CreatePartInput:
    return CreatePartInput(
        sku=sku,
        name=name,
        category=category,
        unit_price=Decimal(unit_price),
        stock_quantity=stock_quantity,
        is_listed=is_listed,
        socket=socket,
        tdp_watts=tdp_watts,
        memory_type=memory_type,
        form_factor=form_factor,
        memory_slot_count=memory_slot_count,
        sata_port_count=sata_port_count,
        m2_slot_count=m2_slot_count,
        module_count=module_count,
        capacity_gb=capacity_gb,
        length_mm=length_mm,
        interface=interface,
        wattage=wattage,
        max_gpu_length_mm=max_gpu_length_mm,
        max_cooler_height_mm=max_cooler_height_mm,
        height_mm=height_mm,
    )
