from django.urls import path

from .views import (
    create_ticket_view,
    get_tickets_view,
    get_ticket_detail_view,
    check_duplicates_view,
    preview_classify_view,
    agent_queue_view,
    classification_override_view,
    transition_ticket_status_view,
    add_ticket_comment_view,
    ticket_timeline_view,
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
        "check-duplicates/",
        check_duplicates_view,
        name="check-duplicates"
    ),
    path(
        "preview-classify/",
        preview_classify_view,
        name="preview-classify"
    ),

    path(
        "queue/",
        agent_queue_view,
        name="agent-queue"
    ),

    path(
        "classifications/<str:ticket_id>/",
        classification_override_view,
        name="classification-override",
    ),

    path(
        "<str:ticket_id>/status/",
        transition_ticket_status_view,
        name="ticket-status-transition",
    ),

    path(
        "<str:ticket_id>/comments/",
        add_ticket_comment_view,
        name="add-ticket-comment",
    ),

    path(
        "<str:ticket_id>/timeline/",
        ticket_timeline_view,
        name="ticket-timeline",
    ),

    path(
        "<str:ticket_id>/",
        get_ticket_detail_view,
        name="ticket-detail"
    ),
    
]