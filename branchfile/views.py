from typing import Any

from django.views import View
from django.views.generic import TemplateView
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import FormMixin
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin, SingleTableView

import branchfile.forms as branchfile_forms

from .filters import BranchFileBranchsFilter
from .models import BranchFile
from .tables import BranchFileBranchsDownloadFilesTable, BranchFileUploadRecordsTable


class BranchFileHomeView(TemplateView):
    template_name = "branchfile_grid.html"


class BranchFileUploadFilesView(TemplateView):
    template_name = "branchfile_upload_files.html"
    form_list = [
        ("form_a", branchfile_forms.HealthInsuranceForm, "prefix_a"),
        ("form_b", branchfile_forms.PaymentNotificationForm, "prefix_b"),
        ("form_c", branchfile_forms.WithholdingCertificateForm, "prefix_c"),
        ("form_d", branchfile_forms.DetailedPaidAmountStatementForm, "prefix_d"),
        ("form_e", branchfile_forms.BreakdownOfItemsTableForm, "prefix_e"),
    ]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        for form_name, form_class, prefix in self.form_list:
            context[form_name] = form_class(prefix=prefix)
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        context = self.get_context_data(*args, **kwargs)
        for form_name, form_class, prefix in self.form_list:
            if prefix in request.POST:
                form = form_class(request.POST, request.FILES, prefix=prefix)

                if form.is_bound:
                    if form.is_valid():
                        form.save()
                    else:
                        context[form_name] = form
        return self.render_to_response(context)

    # table_class = BranchFileUploadRecordsTable
    # model = BranchFile


class BranchFileBranchsListView(TemplateView):
    # class BranchFileBranchsListView(SingleTableMixin, FilterView):
    template_name = "branchfile_branchs_list.html"
    filterset_class = BranchFileBranchsFilter
    table_class = BranchFileBranchsDownloadFilesTable
