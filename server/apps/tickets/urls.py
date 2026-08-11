from django.urls import path

from .views import (
    create_ticket_view,
    get_tickets_view,
    get_ticket_detail_view,
)


urlpatterns = [
    path(
        "",
        create_ticket_view,
        name="create-ticket"
    ),

    path(
        "my/",
        get_tickets_view,
        name="my-tickets"
    ),

    path(
        "<str:ticket_id>/",
        get_ticket_detail_view,
        name="ticket-detail"
    ),
]