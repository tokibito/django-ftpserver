"""
URL configuration for example_project.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, re_path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    re_path(r"^(?P<path>.*)$", views.serve_data_file, name="serve_data_file"),
]
