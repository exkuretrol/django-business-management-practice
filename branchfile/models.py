import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import File


class BranchFileTypeChoices(models.IntegerChoices):
    HEALTH_INSURANCE_DECLARATION_SUMMARY = 1, _("健保申報總表")
    PAYMENT_NOTIFICATION = 2, _("付款通知書")
    WITHHOLDING_CERTIFICATE = 3, _("扣繳憑單")
    DETAILED_PAID_AMOUNT_STATEMENT = 4, _("實付金額明細表")
    BREAKDOWN_OF_ITEMS_TABLE = 5, _("分列項目表")


class ResultChoices(models.IntegerChoices):
    SUCCESS = 1, _("成功")
    FAIL = 2, _("失敗")


class BranchFile(models.Model):
    uuid = models.UUIDField(
        verbose_name=_("UUID"), default=uuid.uuid4, editable=False, primary_key=True
    )
    type = models.PositiveSmallIntegerField(
        verbose_name=_("類別"), choices=BranchFileTypeChoices.choices, editable=False
    )
    attachment = models.ForeignKey(
        to=File,
        on_delete=models.CASCADE,
        verbose_name=_("附件"),
        null=True,
        blank=True,
        default=None,
        editable=False,
    )
    # null is possible when the upload request is failed
    original_filename = models.TextField(
        verbose_name=_("原始檔名"), editable=False, null=True
    )
    declaration_date = models.DateField(verbose_name=_("申報日期"), editable=False)
    result = models.PositiveSmallIntegerField(
        verbose_name=_("結果"),
        editable=False,
        choices=ResultChoices.choices,
        default=ResultChoices.SUCCESS,
    )

    is_latest = models.BooleanField(
        verbose_name=_("是否最新"),
        editable=False,
        default=True,
        help_text=_("是否為最新的檔案"),
    )
    branch = models.ForeignKey(
        to="member.Organization",
        on_delete=models.CASCADE,
        verbose_name=_("門市"),
        editable=False,
    )
    uploaded_at = models.DateTimeField(
        verbose_name=_("上傳時間"),
        auto_now_add=True,
    )

    # possible reason for failure:
    # 1. "The file extension is not allowed."
    # 2. "The file is too large."
    # 3. "The file is empty."

    reason = models.JSONField(
        verbose_name=_("失敗原因"), blank=True, null=True, editable=False
    )

    class Meta:
        verbose_name = _("門市檔案")
        verbose_name_plural = _("門市檔案")
