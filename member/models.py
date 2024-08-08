import uuid

from django.contrib.auth.models import User
from django.db import models


class Organization(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, verbose_name="組織UUID"
    )
    cost_center = models.CharField(
        max_length=20, verbose_name="成本中心", blank=True, default=""
    )
    sno = models.CharField(
        max_length=20, verbose_name="藥局代號", blank=True, default=""
    )
    name = models.CharField(max_length=128, verbose_name="組織名稱")
    short_name = models.CharField(max_length=128, verbose_name="組織簡稱")
    bno = models.CharField(
        max_length=20, verbose_name="藥局統編", blank=True, default=""
    )
    taxno = models.CharField(
        max_length=20, verbose_name="藥局稅籍編號", blank=True, default=""
    )
    org_code = models.CharField(
        max_length=20, verbose_name="藥局醫事機構代號", blank=True, default=""
    )
    person_in_charge = models.CharField(
        max_length=10, verbose_name="藥局負責人", blank=True, default=""
    )
    reg_address = models.CharField(
        max_length=256, verbose_name="藥局登記地址", blank=True, default=""
    )
    contact = models.CharField(
        max_length=10, verbose_name="藥局實際聯絡人", blank=True, default=""
    )
    tel = models.CharField(max_length=20, verbose_name="電話", blank=True, default="")
    fax = models.CharField(max_length=20, verbose_name="傳真", blank=True, default="")
    band_code = models.CharField(
        max_length=10, verbose_name="藥局銀行代號", blank=True, default=""
    )
    band_account = models.CharField(
        max_length=30, verbose_name="藥局銀行帳戶", blank=True, default=""
    )
    is_store = models.BooleanField(default=False, verbose_name="是否為門市")

    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    update_datetime = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "所屬組織"
        verbose_name = "所屬組織"


class Member(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, verbose_name="UUID")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    employee_id = models.CharField(
        max_length=30, verbose_name="員工編號", blank=True, default=""
    )
    org = models.ForeignKey(
        Organization, on_delete=models.CASCADE, verbose_name="所屬組織"
    )
    department = models.CharField(
        max_length=128, verbose_name="部門名稱", blank=True, default=""
    )
    unit = models.CharField(
        max_length=128, verbose_name="單位名稱", blank=True, default=""
    )
    address = models.CharField(
        max_length=128, verbose_name="地址", blank=True, default=""
    )
    tel = models.CharField(max_length=128, verbose_name="電話", blank=True, default="")
    mobile = models.CharField(
        max_length=128, verbose_name="手機", blank=True, default=""
    )
    bank_account = models.CharField(
        max_length=128, verbose_name="對應帳戶", blank=True, default=""
    )

    stop_reason = models.CharField(
        max_length=30, verbose_name="停用原因", blank=True, default=""
    )

    password_hash = models.CharField(
        max_length=256, verbose_name="本次密碼Hash", blank=True, default=""
    )
    password_changetime = models.CharField(
        max_length=30, verbose_name="本次密碼變更時間", blank=True, default=""
    )
    password_hash2 = models.CharField(
        max_length=256, verbose_name="上次密碼Hash", blank=True, default=""
    )
    password_changetime2 = models.CharField(
        max_length=30, verbose_name="上次密碼變更時間", blank=True, default=""
    )
    password_hash3 = models.CharField(
        max_length=256, verbose_name="上上次密碼Hash", blank=True, default=""
    )
    password_changetime3 = models.CharField(
        max_length=30, verbose_name="上上次密碼變更時間", blank=True, default=""
    )

    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    update_datetime = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    def __str__(self):
        return self.user.first_name

    def get_mask_name(self):
        if len(self.user.first_name) < 3:
            return "X"

        masked = (
            self.user.first_name[0]
            + len(self.user.first_name[1:-1]) * "X"
            + self.user.first_name[-1:]
        )
        return masked

    def get_group(self):
        gus = GroupUser.objects.filter(user=self.user)
        if gus.count() > 0:
            return gus[0].group

    class Meta:
        verbose_name_plural = "使用者資料"
        verbose_name = "使用者資料"


class AccessGroup(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, verbose_name="UUID")
    name = models.CharField(max_length=30, verbose_name="群組名稱")

    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    update_datetime = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name_plural = "權限群組"
        verbose_name = "權限群組"


FUNC_CHOICES = [
    ("A01", "公告管理-公告欄設定"),
    ("A02", "公告管理-總部查看公告欄"),
    ("A03", "公告管理-門市查看公告欄"),
    ("B01", "CheckList-CheckList設定"),
    ("C01", "日結進退貨-進貨單上傳"),
]


class GroupFunc(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, verbose_name="UUID")
    group = models.ForeignKey(AccessGroup, on_delete=models.CASCADE)
    func = models.CharField(max_length=3, verbose_name="對應功能", choices=FUNC_CHOICES)

    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    update_datetime = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name_plural = "群組功能"
        verbose_name = "群組功能"


class GroupUser(models.Model):
    group = models.ForeignKey(AccessGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    update_datetime = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        verbose_name_plural = "群組人員"
        verbose_name = "群組人員"


class UserLoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    from_ip = models.CharField(
        max_length=30, verbose_name="來源IP", blank=True, default=""
    )
    content = models.TextField(default="", verbose_name="Log content", blank=True)
    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")

    def __str__(self):
        return self.user.first_name
