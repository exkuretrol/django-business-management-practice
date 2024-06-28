from django.urls import path
from django.views.generic import TemplateView

from .views import ChecklistCreateView

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="checklist_grid.html"),
        name="checklist_grid",
    ),
    path("create/", ChecklistCreateView.as_view(), name="checklist_create"),
]
