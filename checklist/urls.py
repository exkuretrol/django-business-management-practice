from django.urls import path
from django.views.generic import TemplateView

from checklist import views

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="checklist_grid.html"),
        name="checklist_grid",
    ),
    path(
        "create/",
        views.ChecklistCreateView.as_view(),
        name="checklist_create",
    ),
    path("list/", views.ChecklistListView.as_view(), name="checklist_list"),
    path(
        "update/<uuid:pk>/",
        views.ChecklistUpdateView.as_view(),
        name="checklist_update",
    ),
    path(
        "delete/<uuid:pk>/",
        views.ChecklistDeleteView.as_view(),
        name="checklist_delete",
    ),
    path(
        "export/",
        views.ChecklistExportView.as_view(),
        name="checklist_export",
    ),
    path(
        "export/csv/",
        views.ChecklistExportCSVView.as_view(),
        name="checklist_export_csv",
    ),
    path(
        "export/temporary/",
        views.ChecklistTempraryExportView.as_view(),
        name="checklist_temporary_export",
    ),
    path(
        "export/temporary/csv/",
        views.ChecklistTemporaryExportCSVView.as_view(),
        name="checklist_temporary_export_csv",
    ),
]
