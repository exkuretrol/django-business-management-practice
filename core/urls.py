from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("login", auth_views.LoginView.as_view(), name="login"),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
]
