from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    TemplateView,
    UpdateView,
)
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from .filters import AnnouncementBranchsFilter, AnnouncementFilter
from .forms import AnnouncementCreateForm, AnnouncementUpdateForm
from .models import Announcement, AnnouncementAttachment
from .tables import AnnouncementBranchsTable, AnnouncementTable


class AnnouncementHomeView(TemplateView):
    """
    管理公告的首頁。
    """

    template_name = "announcement_grid.html"


class AnnouncementCreateView(LoginRequiredMixin, CreateView):
    """
    新增公告的頁面。

    新增成功後導向到公告列表 :view:`announcement.views.AnnouncementBranchsListView` 頁面。
    """

    form_class = AnnouncementCreateForm
    template_name = "announcement_create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.last_modified_by = self.request.user
        files = form.cleaned_data.get("attachments")
        obj = form.save()

        for f in files:
            # create and save the attachment object to the database,
            # then manually add it to the announcement
            AnnouncementAttachment.objects.create(
                name=f.name, attachment=f, create_datetime=timezone.now()
            )
            obj.attachments.add(AnnouncementAttachment.objects.last())

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("announcement:branchs_list")


class AnnouncementCreateFromCopyView(AnnouncementCreateView):
    """
    從現有公告複製一份新的公告。

    繼承自 :view:`announcement.views.AnnouncementCreateView`。

    這個 View 會在 GET request 時，將原本的公告的標題和內容填入表單中。
    """

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        uuid = self.kwargs.get("uuid")
        announcement = Announcement.objects.get(uuid=uuid)
        context["form"] = AnnouncementCreateForm(
            initial={"title": announcement.title, "content": announcement.content}
        )
        return context


class AnnouncementBranchsListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    """
    所有門市公告列表頁面。

    這個頁面會顯示所有公告，並且可以透過篩選器過濾公告。篩選器的功能包含篩選公告的生效日期、狀態、門市等。

    可以透過 api 來更新公告狀態，如下所示：

    .. code-block:: bash

        curl -X POST -H "Content-Type: application/json" -d '{"announcements": ["<UUID-1>", "<UUID-2>"], "action": "publish"}' http://localhost:8000/api/announcement/action

    這個指令會將 UUID 為 UUID-1, UUID-2 的公告狀態更新為已發佈。
    """

    table_class = AnnouncementBranchsTable
    filterset_class = AnnouncementBranchsFilter
    context_table_name = "announcement_table"
    template_name = "announcement_branchs_list.html"


class AnnouncementListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    """
    單門市公告列表頁面。

    這個頁面會顯示目前帳號關聯的門市的所有公告，並且可以透過篩選器過濾公告。
    篩選器的功能包含篩選公告的標題、狀態等。
    """

    table_class = AnnouncementTable
    filterset_class = AnnouncementFilter
    context_table_name = "announcement_table"
    template_name = "announcement_list.html"


class AnnouncementDetailView(DetailView):
    """
    公告詳細頁面。

    這個頁面會顯示公告的詳細資訊，包含標題、內容、附件等。
    """

    model = Announcement
    template_name = "announcement_detail.html"
    context_object_name = "announcement"


class AnnouncementUpdateView(UpdateView):
    """
    公告更新頁面。

    這個頁面可以更新公告的標題、內容、發佈門市、公告狀態與生效日期起訖日等。
    成功更新後會導向到公告列表 :view:`announcement.views.AnnouncementBranchsListView` 頁面。

    目前沒有辦法編輯公告的附件，如果需要更新附件，請刪除原本的公告，再新增一個新的公告。
    """

    model = Announcement
    form_class = AnnouncementUpdateForm
    template_name = "announcement_update.html"

    def get_success_url(self):
        return reverse("announcement:branchs_list")

    def form_valid(self, form: AnnouncementUpdateForm):
        self.object = form.save(user=self.request.user)
        return HttpResponseRedirect(self.get_success_url())


class AnnouncementDeleteView(DeleteView):
    """
    公告刪除確認頁面。

    這個頁面會提示使用者確認是否要刪除公告，如果使用者確認刪除，則會刪除公告。
    成功刪除後會導向到公告列表 :view:`announcement.views.AnnouncementBranchsListView` 頁面。

    """

    model = Announcement
    template_name = "announcement_delete.html"

    def get_success_url(self):
        return reverse("announcement:branchs_list")
