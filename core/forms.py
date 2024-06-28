from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


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
