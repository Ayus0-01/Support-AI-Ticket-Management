from django.urls import path
from .views import (
    register,
    login,
    me,
    admin_users_view,
    admin_user_detail_view,
)

urlpatterns = [
    path("register/", register),
    path("login/", login),
    path("me/", me),
    path("admin/users/", admin_users_view),
    path("admin/users/<str:user_id>/", admin_user_detail_view),
]