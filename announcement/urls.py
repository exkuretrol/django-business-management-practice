from django.urls import path

from .views import (
    AnnouncementCreateView,
    AnnouncementDeleteView,
    AnnouncementDetailView,
    AnnouncementListView,
    AnnouncementUpdateView,
)

urlpatterns = [
    path("create/", AnnouncementCreateView.as_view(), name="announcement_create"),
    path("list/", AnnouncementListView.as_view(), name="announcement_list"),
    path("<int:pk>/", AnnouncementDetailView.as_view(), name="announcement_detail"),
    path(
        "<int:pk>/update/", AnnouncementUpdateView.as_view(), name="announcement_update"
    ),
    path(
        "<int:pk>/delete/", AnnouncementDeleteView.as_view(), name="announcement_delete"
    ),
]
