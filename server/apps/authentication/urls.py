from django.urls import path
from .views import admin_user_detail, admin_users, login, me, register, resend_verification_email, verify_email

urlpatterns = [
    path("admin/users/", admin_users, name="admin-users"),
    path("admin/users/<str:user_id>/", admin_user_detail, name="admin-user-detail"),
    path("register/", register),
    path("verify-email/", verify_email),
    path("resend-verification/", resend_verification_email),
    path("login/", login),
    path("me/", me),
]
