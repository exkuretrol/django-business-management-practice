from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Layout, Submit
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.forms import FileCleanMixin
from core.models import File, SourceChoices
from core.widgets import YearMonthWidget
from member.models import Member, Organization

from .models import BranchFile, BranchFileTypeChoices


def get_year_choices():
    this_year = timezone.now().year
    years = range(this_year - 1, this_year + 1)
    return years


class BranchFileUploadFileBaseForm(FileCleanMixin, forms.ModelForm):
    form_title = _("上傳檔案")
    type = forms.ChoiceField(
        choices=BranchFileTypeChoices.choices,
        label=_("檔案類型"),
        widget=forms.HiddenInput(),
    )

    declaration_date = forms.DateField(
        label=_("申報年月"),
        widget=YearMonthWidget(years=get_year_choices()),
        initial=timezone.now() - timezone.timedelta(weeks=4),
    )

    class Meta:
        model = File
        fields = ["name", "file", "extension"]
        widgets = {
            "extension": forms.HiddenInput(),
            "name": forms.HiddenInput(),
            "file": forms.FileInput(attrs={"accept": ".pdf,.jpg,.html"}),
        }
        help_texts = {"file": _("可接受的檔案副檔名：pdf, jpg, html")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.keys():
            if field in ["name", "extension"]:
                self.fields[field].required = False
        helper = FormHelper()
        helper.form_id = "file_upload_form"
        helper.layout = Layout(
            HTML(f"<h4>{self.form_title}</h4>"),
            "declaration_date",
            "file",
            Submit(name=self.prefix, value=_("確認上傳")),
        )
        helper.render_hidden_fields = True
        self.helper = helper

    def clean(self):
        cleaned_data = super().clean()
        f = cleaned_data.get("file", None)
        if f is None:
            return cleaned_data

        if "." not in f.name:
            cleaned_data["extension"] = None
        else:
            cleaned_data["extension"] = f.name.rsplit(".", 1)[1]

        if cleaned_data.get("name") == "":
            cleaned_data["name"] = f.name.rsplit(".", 1)[0]

        return cleaned_data

    def save(self, user=None, commit=True):
        f = super().save(commit=False)
        type_label = BranchFileTypeChoices(int(self.cleaned_data["type"])).label

        branch = user.member_set.first().org

        if branch is None:
            raise ValueError(_("使用者沒有所屬門市"))

        branch_label = branch.short_name
        f_original_name = f.name + "." + f.extension if f.extension else f.name
        f.name = f"{type_label}_{branch_label}_{self.cleaned_data['declaration_date'].strftime('%Y%m')}"
        f.source = SourceChoices.BRANCH_FILE
        f.save()

        previous_latest = BranchFile.objects.filter(
            branch=branch, type=self.cleaned_data["type"], is_latest=True
        )

        if previous_latest.exists():
            previous_latest.update(is_latest=False)

        bf = BranchFile(
            original_filename=f_original_name,
            attachment=f,
            type=self.cleaned_data["type"],
            declaration_date=self.cleaned_data["declaration_date"],
            branch=branch,
        )

        bf.save()
        return f


class HealthInsuranceForm(BranchFileUploadFileBaseForm):
    form_title = "健保申報總表"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["type"] = (
            BranchFileTypeChoices.HEALTH_INSURANCE_DECLARATION_SUMMARY
        )


class PaymentNotificationForm(BranchFileUploadFileBaseForm):
    form_title = "付款通知書"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["type"] = BranchFileTypeChoices.PAYMENT_NOTIFICATION


class WithholdingCertificateForm(BranchFileUploadFileBaseForm):
    form_title = "扣繳憑單"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["type"] = BranchFileTypeChoices.WITHHOLDING_CERTIFICATE


class DetailedPaidAmountStatementForm(BranchFileUploadFileBaseForm):
    form_title = "實付金額明細表"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["type"] = BranchFileTypeChoices.DETAILED_PAID_AMOUNT_STATEMENT


class BreakdownOfItemsTableForm(BranchFileUploadFileBaseForm):
    form_title = "分列項目表"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["type"] = BranchFileTypeChoices.BREAKDOWN_OF_ITEMS_TABLE


class BranchsCleanMixin:
    def clean_branchs(self):
        branchs = self.cleaned_data["branchs"]
        if "00000000-0000-0000-0000-000000000000" in branchs:
            if len(branchs) > 1:
                self.add_error("branchs", _("不能同時選擇所有門市與其他門市"))
            return Organization.objects.filter(is_store=True)
        branchs = Organization.objects.filter(pk__in=branchs)
        return branchs


class BranchFileFilterForm(BranchsCleanMixin, forms.Form):
    pass
