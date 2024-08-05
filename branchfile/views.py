import zipfile
from io import BytesIO

from django.http import FileResponse, HttpResponseBadRequest
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DeleteView, ListView, TemplateView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

import branchfile.forms as branchfile_forms
from core.models import File

from .filters import BranchFileBranchsFilter
from .models import BranchFile, ResultChoices
from .tables import BranchFileBranchsDownloadFilesTable, BranchFileUploadRecordsTable


class BranchFileHomeView(TemplateView):
    template_name = "branchfile_grid.html"


class BranchFileUploadFilesView(SingleTableMixin, ListView):
    template_name = "branchfile_upload_files.html"
    table_class = BranchFileUploadRecordsTable
    context_table_name = "records_table"
    model = BranchFile
    paginate_by = 10

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(branch=self.request.user.member_set.first().org)
        )

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
        self.object_list = self.get_queryset()
        context = self.get_context_data(*args, **kwargs)

        u = request.user
        branch = u.member_set.first().org

        if branch is None:
            raise ValueError("User does not have a branch")

        for form_name, form_class, prefix in self.form_list:
            if prefix in request.POST:
                form = form_class(request.POST, request.FILES, prefix=prefix)

                if form.is_bound:
                    if form.is_valid():
                        form.save(user=u)

                    else:
                        bf = BranchFile(
                            reason=form.errors.as_json(),
                            attachment=None,
                            result=ResultChoices.FAIL,
                            declaration_date=form.cleaned_data["declaration_date"],
                            branch=branch,
                            type=form.cleaned_data["type"],
                        )
                        bf.save()
                        context[form_name] = form

                    # update queryset, so that the table is updated
                    context.update(
                        {
                            self.context_table_name: BranchFileUploadRecordsTable(
                                self.object_list
                            )
                        }
                    )
        return self.render_to_response(context)

    # table_class = BranchFileUploadRecordsTable
    # model = BranchFile


class BranchFileBranchsListView(SingleTableMixin, FilterView):
    template_name = "branchfile_branchs_list.html"
    filterset_class = BranchFileBranchsFilter
    table_class = BranchFileBranchsDownloadFilesTable
    context_table_name = "branchs_table"


class BranchFileDeleteView(DeleteView):
    model = File
    template_name = "branchfile_delete.html"
    context_object_name = "file"

    def get_success_url(self):
        return reverse("branchfile:upload_files")


def download_export_zip(request):
    dir_reference = {
        "health_insurance_file_list": "健保申報總表",
        "payment_notification_file_list": "付款通知書",
        "withholding_certificate_file_list": "扣繳憑單",
        "detailed_paid_amount_statement_file_list": "實付金額明細表",
        "breakdown_of_items_table_file_list": "分列項目表",
    }
    files_dict = request.session.get("files_dict", None)
    if files_dict is None:
        return HttpResponseBadRequest("No files_dict in session")
    counter = 0
    for key, value in files_dict.items():
        if not isinstance(value, list):
            return HttpResponseBadRequest(f"Value of {key} is not a list")
        counter += len(value)

    if counter == 0:
        return HttpResponseBadRequest("No files in files_dict")

    bytes_data = BytesIO()
    zip_file = zipfile.ZipFile(bytes_data, "w")

    for key, value in files_dict.items():
        files = File.objects.filter(pk__in=value)
        for f in files:
            file_name = f.name + "." + f.extension if f.extension else f.name
            new_file_name = f"{dir_reference[key]}/{file_name}"
            zip_file.write(f.file.path, arcname=new_file_name)
    zip_file.close()
    bytes_data.seek(0)

    # output filename
    # YYYYMMDD_HHmmss_門市上傳檔案.zip
    return FileResponse(
        bytes_data,
        as_attachment=True,
        filename=f"{timezone.localtime().strftime('%Y%m%d_%H%M%S')}_門市上傳檔案.zip",
    )
