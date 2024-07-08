from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Button, Div, Layout, Submit
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView, FormView, UpdateView
from django_filters.views import FilterView

from core.utils import my_reverse

from .filters import ChecklistBranchFilter, ChecklistFilter, ChecklistTemporaryFilter
from .forms import ChecklistTemplateCreateForm, ChecklistTemplateUpdateForm
from .models import ChecklistTemplate


class ChecklistCreateView(FormView):
    form_class = ChecklistTemplateCreateForm
    template_name = "checklist_create.html"
    success_url = reverse_lazy("checklist_home")

    def form_valid(self, form):
        form.save(user=self.request.user)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class ChecklistListView(LoginRequiredMixin, FilterView):
    filterset_class = ChecklistBranchFilter
    template_name = "checklist_list.html"

    def get_context_data(self, *args, **kwargs):
        # set current branch to session
        self.request.session["current_branch"] = self.request.GET.get("branch", "")
        context = super().get_context_data(**kwargs)
        context["checkbox_checkable"] = False
        return context


class ChecklistTemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = ChecklistTemplate
    template_name = "checklist_template_update.html"
    form_class = ChecklistTemplateUpdateForm
    context_object_name = "checklist_template"

    def get_success_url(self) -> str:
        current_branch = self.request.session.get("current_branch", "")
        return my_reverse("checklist_list", query_kwargs={"branch": current_branch})


class ChecklistTemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = ChecklistTemplate
    template_name = "checklist_template_delete.html"
    context_object_name = "checklist_template"

    def get_context_data(self, *args, **kwargs):
        branchs = self.object.branchs.all()
        if branchs.count() == 0:
            branchs_html = "<span class='badge rounded_pill bg-info'>所有門市</span>"
        else:
            branchs_html = [
                f"<span class='badge rounded_pill bg-info'>{branch.name}</span>"
                for branch in branchs
            ]

        context = super().get_context_data(**kwargs)
        form = context["form"]
        helper = FormHelper()
        helper.layout = Layout(
            HTML(f"<p>確定要刪除 <strong>{self.object}</strong> 嗎？</p>"),
            HTML(f"<p class='mb-0'>會影響到下列門市：</p>"),
            HTML(
                f"<div class='d-flex flex-row gap-2 mb-2'>{''.join(branchs_html)}</div>"
            ),
            Div(
                Submit("submit", "刪除"),
                Button("cancel", "取消", onclick="history.back();"),
                css_class="d-flex gap-2",
            ),
        )
        form.helper = helper
        return context

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_success_url(self) -> str:
        current_branch = self.request.session.get("current_branch", "")
        return my_reverse("checklist_list", query_kwargs={"branch": current_branch})


class ChecklistExportView(LoginRequiredMixin, FilterView):
    filterset_class = ChecklistFilter
    template_name = "checklist_export.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sorted_data"] = self.filterset.qs.order_by(
            "branch", "template_id__priority"
        )
        return context


class ChecklistExportCSVView(ChecklistExportView):
    template_name = "checklist_export_csv.html"
    content_type = "text/csv"


class ChecklistTempraryExportView(LoginRequiredMixin, FilterView):
    filterset_class = ChecklistTemporaryFilter
    template_name = "checklist_temporary_export.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        import pandas as pd

        qs = self.filterset.qs
        data = qs.values(
            "branch__name", "template_id", "template_id__content", "status"
        )
        if len(data) == 0:
            context["pivot_df"] = None
            return context
        df = pd.DataFrame(data)
        pivot_df = df.pivot(
            index="branch__name",
            columns=["template_id", "template_id__content"],
            values="status",
        )
        context["pivot_df"] = pivot_df.to_dict(orient="split")
        return context


class ChecklistTemporaryExportCSVView(ChecklistTempraryExportView):
    template_name = "checklist_temporary_export_csv.html"
    content_type = "text/csv"
