from django.urls import URLPattern, path

from application.api.views.configuration import configuration_evaluate
from application.api.views.csrf import csrf_show
from application.api.views.current_user import current_user_show
from application.api.views.order import order_list, order_show
from application.api.views.part import part_list, part_show
from application.api.views.registration import registration_create
from application.api.views.session import session_create
from application.api.views.staff_order import (
    staff_order_cancel,
    staff_order_list,
    staff_order_prepare,
    staff_order_ship,
    staff_order_show,
)
from application.api.views.staff_part import staff_part_list, staff_part_show

urlpatterns: list[URLPattern] = [
    path("csrf", csrf_show, name="csrf_show"),
    path("registrations", registration_create, name="registration_create"),
    path("sessions", session_create, name="session_create"),
    path("current-user", current_user_show, name="current_user_show"),
    path("parts", part_list, name="part_list"),
    path("parts/<int:part_id>", part_show, name="part_show"),
    path("staff/parts", staff_part_list, name="staff_part_list"),
    path("staff/parts/<int:part_id>", staff_part_show, name="staff_part_show"),
    path(
        "configurations/evaluations",
        configuration_evaluate,
        name="configuration_evaluate",
    ),
    path("orders", order_list, name="order_list"),
    path("orders/<uuid:public_id>", order_show, name="order_show"),
    path("staff/orders", staff_order_list, name="staff_order_list"),
    path("staff/orders/<uuid:public_id>", staff_order_show, name="staff_order_show"),
    path(
        "staff/orders/<uuid:public_id>/prepare",
        staff_order_prepare,
        name="staff_order_prepare",
    ),
    path(
        "staff/orders/<uuid:public_id>/ship",
        staff_order_ship,
        name="staff_order_ship",
    ),
    path(
        "staff/orders/<uuid:public_id>/cancel",
        staff_order_cancel,
        name="staff_order_cancel",
    ),
]
