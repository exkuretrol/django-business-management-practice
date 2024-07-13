from django.urls import path
from django.views.generic import TemplateView

from announcement import views

app_name = "announcement"

urlpatterns = [
    path(
        "",
        views.AnnouncementHomeView.as_view(),
        name="index",
    ),
    path("create/", views.AnnouncementCreateView.as_view(), name="create"),
    path(
        "create/<uuid:uuid>/",
        views.AnnouncementCreateFromCopyView.as_view(),
        name="create_from_copy",
    ),
    path(
        "branchslist/",
        views.AnnouncementBranchsListView.as_view(),
        name="branchs_list",
    ),
    path("list/", views.AnnouncementListView.as_view(), name="list"),
    path("<uuid:pk>/", views.AnnouncementDetailView.as_view(), name="detail"),
    path(
        "update/<uuid:pk>/",
        views.AnnouncementUpdateView.as_view(),
        name="update",
    ),
    path(
        "delete/<uuid:pk>/",
        views.AnnouncementDeleteView.as_view(),
        name="delete",
    ),
]
