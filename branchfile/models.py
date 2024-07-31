from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import File


class BranchFileTypeChoices(models.IntegerChoices):
    HEALTH_INSURANCE_DECLARATION_SUMMARY = 1, _("健保申報總表")
    PAYMENT_NOTIFICATION = 2, _("付款通知書")
    WITHHOLDING_CERTIFICATE = 3, _("扣繳憑單")
    DETAILED_PAID_AMOUNT_STATEMENT = 4, _("實付金額明細表")
    BREAKDOWN_OF_ITEMS_TABLE = 5, _("分列項目表")


class BranchFile(models.Model):
    type = models.PositiveSmallIntegerField(
        verbose_name=_("類別"), choices=BranchFileTypeChoices.choices
    )
    attachment = models.ForeignKey(
        to=File, on_delete=models.CASCADE, verbose_name=_("附件")
    )
    declaration_date = models.DateField(verbose_name=_("申報日期"), editable=False)

    class Meta:
        verbose_name = _("門市檔案")
        verbose_name_plural = _("門市檔案")
