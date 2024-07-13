from django.urls import path
from django.views.generic import TemplateView

from checklist import views

app_name = "checklist"

urlpatterns = [
    path(
        "",
        views.ChecklistHomeView.as_view(),
        name="index",
    ),
    path(
        "create/",
        views.ChecklistCreateView.as_view(),
        name="create",
    ),
    path(
        "branchslist/",
        views.ChecklistBranchsListView.as_view(),
        name="branchs_list",
    ),
    path("list/", views.ChecklistListView.as_view(), name="list"),
    path(
        "update/<int:pk>/",
        views.ChecklistTemplateUpdateView.as_view(),
        name="update",
    ),
    path(
        "delete/<int:pk>/",
        views.ChecklistTemplateDeleteView.as_view(),
        name="delete",
    ),
    path(
        "export/",
        views.ChecklistExportView.as_view(),
        name="export",
    ),
    path(
        "export/csv/",
        views.ChecklistExportCSVView.as_view(),
        name="export_csv",
    ),
    path(
        "export/temporary/",
        views.ChecklistTempraryExportView.as_view(),
        name="temporary_export",
    ),
    path(
        "export/temporary/csv/",
        views.ChecklistTemporaryExportCSVView.as_view(),
        name="temporary_export_csv",
    ),
]
