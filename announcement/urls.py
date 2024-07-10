from django.urls import path
from django.views.generic import TemplateView

from .views import (
    AnnouncementBranchsListView,
    AnnouncementCreateFromCopyView,
    AnnouncementCreateView,
    AnnouncementDeleteView,
    AnnouncementDetailView,
    AnnouncementListView,
    AnnouncementUpdateView,
)

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="announcement_grid.html"),
        name="announcement_home",
    ),
    path("create/", AnnouncementCreateView.as_view(), name="announcement_create"),
    path(
        "create/<uuid:uuid>/",
        AnnouncementCreateFromCopyView.as_view(),
        name="announcement_create_from_copy",
    ),
    path(
        "branchslist/",
        AnnouncementBranchsListView.as_view(),
        name="announcement_branchs_list",
    ),
    path("list/", AnnouncementListView.as_view(), name="announcement_list"),
    path("<uuid:pk>/", AnnouncementDetailView.as_view(), name="announcement_detail"),
    path(
        "<uuid:pk>/update/",
        AnnouncementUpdateView.as_view(),
        name="announcement_update",
    ),
    path(
        "<uuid:pk>/delete/",
        AnnouncementDeleteView.as_view(),
        name="announcement_delete",
    ),
]
