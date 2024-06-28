from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from django.views.generic import FormView
from django_filters.views import FilterView
from django_tables2 import MultiTableMixin

from .filters import ChecklistFilter
from .forms import ChecklistCreateForm
from .models import Checklist
from .tables import ChecklistTable


class ChecklistCreateView(FormView):
    form_class = ChecklistCreateForm
    template_name = "checklist_create.html"
    success_url = reverse_lazy("checklist_grid")

    def form_valid(self, form):
        form.save(commit=True)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class ChecklistListView(LoginRequiredMixin, FilterView):
    filterset_class = ChecklistFilter
    template_name = "checklist_list.html"
