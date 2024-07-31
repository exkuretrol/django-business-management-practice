from django.urls import path

import branchfile.views as views

app_name = "branchfile"
urlpatterns = [
    path("", views.BranchFileHomeView.as_view(), name="home"),
    path(
        "upload/",
        views.BranchFileUploadFilesView.as_view(),
        name="upload_files",
    ),
    path(
        "branchs_list/",
        views.BranchFileBranchsListView.as_view(),
        name="branchs_list",
    ),
]
