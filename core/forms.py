import hashlib

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Hidden, Layout, Submit
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from member.models import Organization

from .models import File

ALL_BRANCHS = "00000000-0000-0000-0000-000000000000"


def get_all_branch_choices(include_all_branch=True):
    l = list(Organization.objects.filter(is_store=True).values_list("pk", "short_name"))
    if include_all_branch:
        l.insert(0, (ALL_BRANCHS, _("所有門市")))
    return l


class BranchsCleanMixin:
    """
    用於需要回傳當所有門市被選取時，回傳 `Organization.objects.all()` 的表單
    """

    def clean_branchs(self):
        branchs = self.cleaned_data["branchs"]
        if ALL_BRANCHS in branchs:
            if len(branchs) > 1:
                self.add_error("branchs", _("不能同時選擇所有門市與其他門市"))
            return Organization.objects.filter(is_store=True)
        branchs = Organization.objects.filter(pk__in=branchs)
        return branchs


class BranchsNoneCleanMixin:
    """
    用於需要回傳當所有門市被選取時，回傳空的 `Organization.objects.none()` 的表單
    """

    def clean_branchs(self):
        branchs = self.cleaned_data["branchs"]
        if ALL_BRANCHS in branchs:
            if len(branchs) > 1:
                self.add_error("branchs", _("不能同時選擇所有門市與其他門市"))
            return Organization.objects.none()
        branchs = Organization.objects.filter(pk__in=branchs)
        return branchs


class LoginForm(AuthenticationForm):
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        form = self
        form.fields["username"].widget.attrs.update({"placeholder": _("使用者名稱")})
        form.fields["password"].widget.attrs.update({"placeholder": _("密碼")})
        helper = FormHelper()
        helper.form_show_labels = False
        helper.layout = Layout(
            "username",
            "password",
            Div(
                Submit("submit", _("登入"), css_class="btn btn-primary btn-block"),
                css_class="mt-5 d-grid",
            ),
        )
        self.helper = helper


class FileCleanMixin:
    def clean(self):
        cleaned_data = super().clean()

        file = cleaned_data.get("file", None)
        sha256_hash = hashlib.sha256()

        f = file.open("rb")
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

        existed_file = File.objects.filter(hash=sha256_hash.hexdigest())

        if existed_file.exists():
            self.add_error(
                "file",
                _(
                    f"檔案已存在。檔案名稱：{existed_file.first().name}。上傳時間：{timezone.localtime(existed_file.first().create_datetime):%Y-%m-%d %H:%M:%S}"
                ),
            )
            f.close()
        return cleaned_data


class FileUploadForm(FileCleanMixin, forms.ModelForm):
    class Meta:
        model = File
        fields = ["name", "file", "extension"]
        widgets = {"extension": forms.HiddenInput()}
        help_texts = {"name": _("檔案名稱。留空則使用檔案原始名稱")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.keys():
            if field in ["name", "extension"]:
                self.fields[field].required = False
        helper = FormHelper()
        helper.form_id = "file_upload_form"
        helper.layout = Layout("name", "file", Hidden("extension", None))
        self.helper = helper

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file", None)
        if file is None:
            self.add_error("file", _("請選擇檔案"))

        if "." not in file.name:
            cleaned_data["extension"] = None
        else:
            cleaned_data["extension"] = file.name.rsplit(".", 1)[1]

        if cleaned_data.get("name") == "" or cleaned_data.get("name") is None:
            cleaned_data["name"] = file.name.rsplit(".", 1)[0]

        return cleaned_data
