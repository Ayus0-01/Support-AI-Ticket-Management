from django.urls import path
from apps.admin_panel.views import admin_overview_view, system_status_view

urlpatterns = [
    path("overview/", admin_overview_view, name="admin-panel-overview"),
    path("system-status/", system_status_view, name="admin-panel-system-status"),
]
