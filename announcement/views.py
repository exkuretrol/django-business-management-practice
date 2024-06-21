from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from .filters import AnnouncementFilter
from .forms import AnnouncementCreateForm
from .models import Announcement, AnnouncementAttachment
from .tables import AnnouncementTable


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


class AnnouncementListView(SingleTableMixin, FilterView):
    table_class = AnnouncementTable
    filterset_class = AnnouncementFilter
    context_table_name = "announcement_table"
    template_name = "announcement_list.html"


class AnnouncementDetailView(DetailView):
    model = Announcement
    template_name = "announcement_detail.html"
    context_object_name = "announcement"


class AnnouncementUpdateView(UpdateView):
    model = Announcement
    form_class = AnnouncementCreateForm
    template_name = "announcement_update.html"

    def get_success_url(self):
        return reverse("announcement_list")


class AnnouncementDeleteView(DeleteView):
    model = Announcement
    template_name = "announcement_delete.html"

    def get_success_url(self):
        return reverse("announcement_list")
