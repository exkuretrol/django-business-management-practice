from typing import Any

from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView

from .forms import LoginForm


class NewLoginView(LoginView):
    form_class = LoginForm


class ExternalLinkView(TemplateView):
    template_name = "external_link.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["link"] = self.request.GET.get("link")
        return context
