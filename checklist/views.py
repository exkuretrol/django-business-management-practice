from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Button, Div, Layout, Submit
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, FormView, UpdateView
from django_filters.views import FilterView

from branch.models import Branch

from .filters import ChecklistFilter
from .forms import ChecklistCreateForm, ChecklistUpdateForm
from .models import Checklist


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

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["checkbox_checkable"] = False
        return context


from django.utils.http import urlencode


def my_reverse(viewname, kwargs=None, query_kwargs=None):
    """
    Custom reverse to add a query string after the url
    Example usage:
    url = my_reverse('my_test_url', kwargs={'pk': object.id}, query_kwargs={'next': reverse('home')})
    """
    url = reverse(viewname, kwargs=kwargs)

    if query_kwargs:
        return f"{url}?{urlencode(query_kwargs)}"

    return url


class ChecklistUpdateView(LoginRequiredMixin, UpdateView):
    model = Checklist
    template_name = "checklist_update.html"
    form_class = ChecklistUpdateForm

    def get_success_url(self) -> str:
        obj = self.get_object()
        branch_pk = obj.branch.pk
        return my_reverse("checklist_list", query_kwargs={"branch": branch_pk})


class ChecklistDeleteView(LoginRequiredMixin, DeleteView):
    model = Checklist
    template_name = "checklist_delete.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        helper = FormHelper()
        helper.layout = Layout(
            HTML(f"<p>確定要刪除 <strong>{self.object}</strong> 嗎？</p>"),
            Div(
                Submit("submit", "刪除"),
                Button("cancel", "取消", onclick="history.back();"),
                css_class="d-flex gap-2",
            ),
        )
        form.helper = helper
        return context

    def get_success_url(self) -> str:
        obj = self.get_object()
        branch_pk = obj.branch.pk
        return my_reverse("checklist_list", query_kwargs={"branch": branch_pk})
