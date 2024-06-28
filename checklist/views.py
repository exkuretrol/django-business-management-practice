from django import forms
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView

from .forms import ChecklistCreateForm
from .models import Checklist, ChecklistTemplate


class ChecklistCreateView(FormView):
    form_class = ChecklistCreateForm
    template_name = "checklist_create.html"
    success_url = reverse_lazy("checklist_grid")

    def form_valid(self, form):
        form.save(commit=True)
        return super().form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response
