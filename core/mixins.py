from django.contrib.auth.mixins import LoginRequiredMixin


class PostModifiedByMixin(LoginRequiredMixin):
    def form_valid(self, form):
        form.instance.last_modified_by = self.request.user
        return super().form_valid(form)
