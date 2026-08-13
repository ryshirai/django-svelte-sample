from decimal import Decimal

from django.core.management.base import BaseCommand

from application.errors.authentication import RegistrationEmailAlreadyUsedError
from application.errors.part import PartSkuAlreadyUsedError
from application.services.part import CreatePartInput, create_part
from application.services.registration import (
    CreateRegistrationInput,
    CreateStaffUserInput,
    create_registration,
    create_staff_user,
)


class Command(BaseCommand):
    help = "Seed catalog parts and development users."

    def handle(self, *args: object, **options: object) -> None:
        del args, options
        _seed_users()
        for item in _catalog_items():
            try:
                create_part(input=item)
            except PartSkuAlreadyUsedError:
                # 既存 SKU は更新せずスキップする。
                continue


def _seed_users() -> None:
    create_staff_user(
        input=CreateStaffUserInput(email="staff@example.com", password="staffpass")
    )
    try:
        create_registration(
            input=CreateRegistrationInput(
                email="buyer@example.com",
                password="buyerpass",
            )
        )
    except RegistrationEmailAlreadyUsedError:
        return


def _catalog_items() -> list[CreatePartInput]:
    # 通る構成 / 意図的に落ちる構成 / 顧客一覧に出ない未掲載。
    return [
        *_compatible_parts(),
        *_incompatible_parts(),
        _hidden_cpu(),
    ]


def _compatible_parts() -> list[CreatePartInput]:
    return [
        _base_part(
            sku="CPU-AM5-7600",
            name="Ryzen 5 7600",
            category="cpu",
            unit_price="24800",
            socket="am5",
            tdp_watts=65,
        ),
        _base_part(
            sku="MB-AM5-ATX",
            name="AM5 ATX Motherboard",
            category="motherboard",
            unit_price="19800",
            socket="am5",
            memory_type="ddr5",
            form_factor="atx",
            memory_slot_count=4,
            sata_port_count=4,
            m2_slot_count=2,
        ),
        _base_part(
            sku="MEM-DDR5-32",
            name="DDR5 32GB",
            category="memory",
            unit_price="12800",
            memory_type="ddr5",
            module_count=2,
            capacity_gb=32,
        ),
        _base_part(
            sku="SSD-M2-1T",
            name="1TB M.2 SSD",
            category="storage",
            unit_price="9800",
            interface="m2",
        ),
        _base_part(
            sku="PSU-650",
            name="650W PSU",
            category="psu",
            unit_price="9800",
            wattage=650,
        ),
        _base_part(
            sku="CASE-ATX",
            name="ATX Mid Tower",
            category="case",
            unit_price="8900",
            form_factor="atx",
            max_gpu_length_mm=360,
            max_cooler_height_mm=160,
        ),
        _base_part(
            sku="GPU-4070",
            name="GeForce RTX 4070",
            category="gpu",
            unit_price="89800",
            length_mm=304,
            tdp_watts=200,
        ),
        _base_part(
            sku="CLR-AM5-155",
            name="AM5 Air Cooler 155mm",
            category="cpu_cooler",
            unit_price="6800",
            socket="am5",
            height_mm=155,
        ),
    ]


def _incompatible_parts() -> list[CreatePartInput]:
    return [
        _base_part(
            sku="CPU-1700-13400",
            name="Core i5-13400",
            category="cpu",
            unit_price="22800",
            socket="lga1700",
            tdp_watts=65,
        ),
        _base_part(
            sku="MEM-DDR4-16",
            name="DDR4 16GB",
            category="memory",
            unit_price="6800",
            memory_type="ddr4",
            module_count=2,
            capacity_gb=16,
        ),
        _base_part(
            sku="CASE-ITX",
            name="ITX Case",
            category="case",
            unit_price="7900",
            form_factor="itx",
            max_gpu_length_mm=280,
            max_cooler_height_mm=140,
        ),
        _base_part(
            sku="PSU-300",
            name="300W PSU",
            category="psu",
            unit_price="4800",
            wattage=300,
        ),
        _base_part(
            sku="GPU-LONG",
            name="Long GPU 400mm",
            category="gpu",
            unit_price="79800",
            length_mm=400,
            tdp_watts=220,
        ),
        _base_part(
            sku="CLR-TALL",
            name="Tall Cooler 180mm",
            category="cpu_cooler",
            unit_price="8800",
            socket="am5",
            height_mm=180,
        ),
    ]


def _hidden_cpu() -> CreatePartInput:
    return _base_part(
        sku="CPU-HIDDEN",
        name="Hidden CPU",
        category="cpu",
        unit_price="19800",
        socket="am5",
        tdp_watts=65,
        is_listed=False,
    )


def _base_part(
    *,
    sku: str,
    name: str,
    category: str,
    unit_price: str,
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
        stock_quantity=10,
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
