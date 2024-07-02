from django.urls import path, re_path
from django.views.generic import TemplateView

from .views import (
    ChecklistCreateView,
    ChecklistDeleteView,
    ChecklistListView,
    ChecklistUpdateView,
)

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="checklist_grid.html"),
        name="checklist_grid",
    ),
    path("create/", ChecklistCreateView.as_view(), name="checklist_create"),
    path("list/", ChecklistListView.as_view(), name="checklist_list"),
    path(
        "update/<int:pk>/",
        ChecklistUpdateView.as_view(),
        name="checklist_update",
    ),
    path(
        "delete/<int:pk>/",
        ChecklistDeleteView.as_view(),
        name="checklist_delete",
    ),
]
