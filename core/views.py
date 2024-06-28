from django.contrib.auth.views import LoginView

from .forms import LoginForm


class NewLoginView(LoginView):
    form_class = LoginForm
