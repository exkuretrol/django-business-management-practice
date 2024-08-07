from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import include, path

from core import views as core_views

from .api import api

urlpatterns = [
    path("", core_views.home, name="home"),
    path(
        "redirect/",
        core_views.ExternalLinkView.as_view(),
        name="external_link",
    ),
    path("api/", api.urls),
    path("accounts/login/", core_views.NewLoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("file/", core_views.update_file, name="upload_file"),
    path("file/<uuid:file_id>/", core_views.download_file, name="download_file"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += (path("__debug__/", include("debug_toolbar.urls")),)
