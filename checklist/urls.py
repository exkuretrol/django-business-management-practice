from django.urls import path, re_path
from django.views.generic import TemplateView

from .views import (
    ChecklistCreateView,
    ChecklistDeleteView,
    ChecklistExportCSVView,
    ChecklistExportView,
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
    path(
        "export/",
        ChecklistExportView.as_view(),
        name="checklist_export",
    ),
    path(
        "export/csv/",
        ChecklistExportCSVView.as_view(),
        name="checklist_export_csv",
    ),
]
