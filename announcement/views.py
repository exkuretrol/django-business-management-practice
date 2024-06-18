from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView

from .forms import AnnouncementCreateForm
from .models import AnnouncementAttachment


class AnnouncementCreateView(CreateView):
    form_class = AnnouncementCreateForm
    template_name = "announcement_create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        files = form.cleaned_data.get("attachments")
        obj = form.save()

        for f in files:
            # create and save the attachment object to the database, then manually add it to the announcement
            AnnouncementAttachment.objects.create(
                name=f.name, attachment=f, create_datetime=timezone.now()
            )
            obj.attachments.add(AnnouncementAttachment.objects.last())

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("home")
