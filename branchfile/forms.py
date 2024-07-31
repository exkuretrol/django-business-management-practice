from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Hidden, Layout, Submit
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.forms import FileCleanMixin
from core.models import File
from core.widgets import YearMonthWidget

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
        initial=timezone.now() - timezone.timedelta(weeks=5),
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

        # TODO: replace with user branch
        branch_label = "台大門市" if user is None else user
        f.name = f"{type_label}_{branch_label}_{self.cleaned_data['declaration_date'].strftime('%Y%m')}"
        f.save()

        bf = BranchFile(
            attachment=f,
            type=self.cleaned_data["type"],
            declaration_date=self.cleaned_data["declaration_date"],
            nth_upload=BranchFile.objects.filter(
                type=self.cleaned_data["type"],
                declaration_date=self.cleaned_data["declaration_date"],
            ).count()
            + 1,
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
