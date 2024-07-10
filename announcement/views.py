from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from .filters import AnnouncementBranchsFilter, AnnouncementFilter
from .forms import AnnouncementCreateForm, AnnouncementUpdateForm
from .models import Announcement, AnnouncementAttachment
from .tables import AnnouncementBranchsTable, AnnouncementTable


class AnnouncementCreateView(LoginRequiredMixin, CreateView):
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
        return reverse("announcement_list")


class AnnouncementCreateFromCopyView(AnnouncementCreateView):
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        uuid = self.kwargs.get("uuid")
        announcement = Announcement.objects.get(uuid=uuid)
        context["form"] = AnnouncementCreateForm(
            initial={"title": announcement.title, "content": announcement.content}
        )
        return context


class AnnouncementBranchsListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    table_class = AnnouncementBranchsTable
    filterset_class = AnnouncementBranchsFilter
    context_table_name = "announcement_table"
    template_name = "announcement_branchs_list.html"


class AnnouncementListView(LoginRequiredMixin, SingleTableMixin, FilterView):
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
    form_class = AnnouncementUpdateForm
    template_name = "announcement_update.html"

    def get_success_url(self):
        return reverse("announcement_list")


class AnnouncementDeleteView(DeleteView):
    model = Announcement
    template_name = "announcement_delete.html"

    def get_success_url(self):
        return reverse("announcement_list")
