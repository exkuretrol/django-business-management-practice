from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Button, Div, Layout, Submit
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Q
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    DeleteView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from django_filters.views import FilterView

from branch.models import Branch
from core.utils import my_reverse

from .filters import ChecklistBranchFilter, ChecklistFilter, ChecklistTemporaryFilter
from .forms import ChecklistTemplateCreateForm, ChecklistTemplateUpdateForm
from .models import Checklist, ChecklistTemplate, StatusChoices


class ChecklistHomeView(TemplateView):
    """
    待做清單首頁。
    """

    template_name = "checklist_grid.html"


class ChecklistCreateView(LoginRequiredMixin, FormView):
    """
    待做清單模板新增頁面。

    新增時，會將新增者設為最後更新者。
    """

    form_class = ChecklistTemplateCreateForm
    template_name = "checklist_create.html"
    success_url = reverse_lazy("checklist:index")

    def form_valid(self, form):
        form.save(user=self.request.user)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class ChecklistBranchsListView(LoginRequiredMixin, FilterView):
    """
    各個門市待做清單列表。

    進入此頁面時，會將當前門市設定到 session 中。供 :view:`checklist.views.ChecklistTemplateUpdateView`
    與 :view:`checklist.views.ChecklistTemplateDeleteView` 使用。會在更新或刪除後導回此頁面。保留當前門市。
    """

    filterset_class = ChecklistBranchFilter
    template_name = "checklist_branchs_list.html"

    def get_context_data(self, *args, **kwargs):
        # set current branch to session
        self.request.session["current_branch"] = self.request.GET.get("branch", "")
        context = super().get_context_data(**kwargs)
        context["checkbox_checkable"] = False
        return context


class ChecklistListView(LoginRequiredMixin, ListView):
    """
    待做清單列表。

    顯示當前門市的待做清單。依照狀態排序，未完成的待做清單會排在前面。
    """

    context_object_name = "checklist"
    template_name = "checklist_list.html"
    model = Checklist

    branch = Branch.objects.first()

    def get_queryset(self):
        today = timezone.now().date()
        qs = super().get_queryset()
        return (
            qs.exclude(is_archived=True)
            .filter(
                branch=self.branch,
                effective_start_date__lte=today,
                effective_end_date__gte=today,
            )
            .annotate(
                priority=F("template_id__priority"), content=F("template_id__content")
            )
            .order_by("priority", "status")
        )

    def get_progress(self):
        qs = self.get_queryset()
        return qs.aggregate(
            count=Count("pk"),
            finished=Count("status", filter=Q(status=True)),
            todo=Count("status", filter=Q(status=False)),
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        progress = self.get_progress()
        progress["finished_percent"] = (
            progress["finished"] / progress["count"] * 100
            if progress["count"] != 0
            else 0
        )
        context["progress"] = progress
        context["checkbox_checkable"] = True
        return context


class ChecklistTemplateUpdateView(LoginRequiredMixin, UpdateView):
    """
    待做清單模板更新頁面。

    更新時，會將更新者設為最後更新者。並導回 :view:`checklist.views.ChecklistBranchsListView`。
    """

    model = ChecklistTemplate
    template_name = "checklist_template_update.html"
    form_class = ChecklistTemplateUpdateForm
    context_object_name = "checklist_template"

    def get_success_url(self) -> str:
        current_branch = self.request.session.get("current_branch", "")
        return my_reverse(
            "checklist:branchs_list", query_kwargs={"branch": current_branch}
        )

    def form_valid(self, form):
        self.object = form.save(user=self.request.user)
        return HttpResponseRedirect(self.get_success_url())


class ChecklistTemplateDeleteView(LoginRequiredMixin, DeleteView):
    """
    待做清單模板刪除頁面。

    刪除時，會將刪除者設為最後更新者。並導回 :view:`checklist.views.ChecklistBranchsListView`。
    """

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
        return my_reverse(
            "checklist:branchs_list", query_kwargs={"branch": current_branch}
        )


class ChecklistExportView(LoginRequiredMixin, FilterView):
    """
    待做清單匯出預覽頁面。

    透過篩選器來過濾待做清單。並依照分店、狀態、優先順序、排序來排序。

    篩選後可以透過 :view:`checklist.views.ChecklistExportCSVView` 匯出成 CSV 檔案。
    """

    filterset_class = ChecklistFilter
    template_name = "checklist_export.html"
    paginate_by = 5

    def get(self, request, *args, **kwargs):
        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)

        if (
            not self.filterset.is_bound
            or self.filterset.is_valid()
            or not self.get_strict()
        ):
            self.object_list = self.filterset.qs
        else:
            self.object_list = self.filterset.queryset.none()
        queryset = self.object_list.values(
            branch_no=F("branch"),
            branch_name=F("branch__name"),
            priority=F("template_id__priority"),
            content=F("template_id__content"),
            last_modified_date=F("last_modified"),
        ).order_by("branch_no", "priority")
        from itertools import groupby
        from operator import itemgetter

        new_qs = groupby(queryset, key=itemgetter("branch_name"))

        self.object_list = [
            {branch_name: list(branch_qs)} for branch_name, branch_qs in new_qs
        ]

        context = self.get_context_data(
            filter=self.filterset, object_list=self.object_list
        )

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ChecklistExportCSVView(ChecklistExportView):
    """
    待做清單匯出 CSV 頁面。

    在 :view:`checklist.views.ChecklistExportView` 的基礎上，將資料匯出成 CSV 檔案。
    """

    template_name = "checklist_export_csv.html"
    content_type = "text/csv"


class ChecklistTempraryExportView(LoginRequiredMixin, FilterView):
    """
    待做清單臨時事項匯出預覽頁面。

    篩選後可以透過 :view:`checklist.views.ChecklistTemporaryExportCSVView` 匯出成 CSV 檔案。
    """

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
    """
    待做清單臨時事項匯出 CSV 頁面。

    在 :view:`checklist.views.ChecklistTempraryExportView` 的基礎上，將資料匯出成 CSV 檔案。
    """

    template_name = "checklist_temporary_export_csv.html"
    content_type = "text/csv"
