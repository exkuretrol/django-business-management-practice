import django_filters as filters
from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.db.models import OuterRef, Prefetch, Subquery, Value
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.forms import get_all_branch_choices
from core.widgets import Tagify, TagifyMultipleChoiceFilter, YearMonthWidget
from member.models import Organization

from .forms import BranchFileFilterForm, get_year_choices
from .models import BranchFile, BranchFileTypeChoices, ResultChoices


class BranchFileBranchsFilter(filters.FilterSet):
    branchs = TagifyMultipleChoiceFilter(
        field_name="branchs",
        label=_("門市"),
        choices=get_all_branch_choices,
        method="filter_branchs",
        required=True,
        widget=Tagify(attrs={"placeholder": _("請選擇門市")}),
    )

    declaration_date = filters.DateFilter(
        field_name="declaration_date",
        label=_("申報年月"),
        widget=YearMonthWidget(years=get_year_choices()),
        required=True,
        method="filter_declaration_date",
        initial=timezone.now() - timezone.timedelta(weeks=4),
    )

    has_uploaded = filters.ChoiceFilter(
        field_name="branchfile__isnull",
        label=_("是否已上傳檔案"),
        choices=[
            ("All", _("全部")),
            ("True", _("有上傳任一檔案")),
            ("False", _("無上傳任何檔案")),
        ],
        empty_label=None,
        widget=forms.RadioSelect,
        initial="All",
        required=True,
        method="filter_has_uploaded",
    )

    def filter_branchs(self, queryset, name, value):
        return queryset.filter(branch__in=value)

    def filter_declaration_date(self, queryset, name, value):
        return queryset.filter(
            declaration_date__year=value.year, declaration_date__month=value.month
        )

    def filter_has_uploaded(self, queryset, name, value):
        declaration_date = self.form.cleaned_data.get("declaration_date")
        has_uploaded_branchs = (
            queryset.filter(result=ResultChoices.SUCCESS)
            .values_list("branch", flat=True)
            .distinct()
        )
        org_with_file = Organization.objects.filter(
            pk__in=has_uploaded_branchs
        ).annotate(
            health_insurance_file=Subquery(
                queryset.filter(
                    branch=OuterRef("pk"),
                    type=BranchFileTypeChoices.HEALTH_INSURANCE_DECLARATION_SUMMARY,
                    is_latest=True,
                ).values("attachment")
            ),
            payment_notification_file=Subquery(
                queryset.filter(
                    branch=OuterRef("pk"),
                    type=BranchFileTypeChoices.PAYMENT_NOTIFICATION,
                    is_latest=True,
                ).values("attachment")
            ),
            withholding_certificate_file=Subquery(
                queryset.filter(
                    branch=OuterRef("pk"),
                    type=BranchFileTypeChoices.WITHHOLDING_CERTIFICATE,
                    is_latest=True,
                ).values("attachment")
            ),
            detailed_paid_amount_statement_file=Subquery(
                queryset.filter(
                    branch=OuterRef("pk"),
                    type=BranchFileTypeChoices.DETAILED_PAID_AMOUNT_STATEMENT,
                    is_latest=True,
                ).values("attachment")
            ),
            breakdown_of_items_table_file=Subquery(
                queryset.filter(
                    branch=OuterRef("pk"),
                    type=BranchFileTypeChoices.BREAKDOWN_OF_ITEMS_TABLE,
                    is_latest=True,
                ).values("attachment")
            ),
            declaration_date=Value(declaration_date),
            last_uploaded_date=Subquery(
                queryset.filter(
                    branch=OuterRef("pk"),
                    is_latest=True,
                )
                .order_by("-uploaded_at")
                .values("uploaded_at")[:1]
            ),
        )

        files_dict = {
            "health_insurance_file_list": [],
            "payment_notification_file_list": [],
            "withholding_certificate_file_list": [],
            "detailed_paid_amount_statement_file_list": [],
            "breakdown_of_items_table_file_list": [],
        }
        for org in org_with_file:
            if org.health_insurance_file:
                files_dict["health_insurance_file_list"].append(
                    str(org.health_insurance_file)
                )
            if org.payment_notification_file:
                files_dict["payment_notification_file_list"].append(
                    str(org.payment_notification_file)
                )
            if org.withholding_certificate_file:
                files_dict["withholding_certificate_file_list"].append(
                    str(org.withholding_certificate_file)
                )
            if org.detailed_paid_amount_statement_file:
                files_dict["detailed_paid_amount_statement_file_list"].append(
                    str(org.detailed_paid_amount_statement_file)
                )
            if org.breakdown_of_items_table_file:
                files_dict["breakdown_of_items_table_file_list"].append(
                    str(org.breakdown_of_items_table_file)
                )

        self.request.session.update({"files_dict": files_dict})

        org_without_file = (
            self.form.cleaned_data.get("branchs")
            .exclude(pk__in=has_uploaded_branchs)
            .annotate(declaration_date=Value(declaration_date))
        )
        # has upload any file
        if value == "True":
            return org_with_file
        # did not upload any file
        elif value == "False":
            return org_without_file
        # all
        else:
            return org_with_file | org_without_file

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        form = self.form
        helper = FormHelper()
        helper.form_method = "get"
        helper.layout = Layout(
            "branchs",
            "declaration_date",
            InlineRadios(
                "has_uploaded",
                template="bootstrap5/radioselect_inline.html",
            ),
            Submit("submit", _("篩選")),
        )
        form.helper = helper

    @property
    def qs(self):
        queryset = super().qs
        branchs = self.request.GET.get("branchs", None)
        if branchs is None:
            return queryset.none()
        return queryset

    class Meta:
        model = BranchFile
        fields = ["branchs", "declaration_date"]
        form = BranchFileFilterForm
