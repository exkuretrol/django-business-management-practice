from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic import TemplateView

from .api import api
from .views import ExternalLinkView, NewLoginView, download_file, update_file

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path(
        "redirect/",
        ExternalLinkView.as_view(),
        name="external_link",
    ),
    path("api/", api.urls),
    path("accounts/login/", NewLoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("file/", update_file, name="upload_file"),
    path("file/<int:pk>/", download_file, name="download_file"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += (path("__debug__/", include("debug_toolbar.urls")),)
