from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import BadRequest, PermissionDenied
from django.http import FileResponse, HttpRequest, JsonResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from member.models import Member

from .forms import FileUploadForm, LoginForm
from .models import File


class NewLoginView(LoginView):
    form_class = LoginForm


@login_required()
def home(request: HttpRequest):
    user = request.user

    branch = Member.objects.filter(user=user).first().org
    if branch.is_store:
        return redirect("announcement:list")
    else:
        return redirect("announcement:branchs_list")


class ExternalLinkView(TemplateView):
    template_name = "external_link.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["link"] = self.request.GET.get("link")
        return context


def update_file(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        else:
            return JsonResponse({"error": form.errors}, status=400)

        return JsonResponse(
            {
                "success": "File uploaded successfully.",
                "object": {
                    "value": str(form.instance.uuid),
                    "label": str(form.instance),
                },
            },
            status=200,
        )


def download_file(request: HttpRequest, file_id: int) -> FileResponse:
    file_ = File.objects.get(pk=file_id)
    filename = file_.name + "." + file_.extension if file_.extension else file_.name
    response = FileResponse(file_.file, as_attachment=True, filename=filename)

    user_group = request.user.groupuser_set.first().group

    if request.user.is_superuser or user_group.name == "總部":
        return response

    user_branch = request.user.member_set.first().org

    if (branchfile_set := file_.branchfile_set.first()) is not None:
        branchfile_branch = branchfile_set.branch
        if user_branch != branchfile_branch:
            raise PermissionDenied
        return response

    # one file may have multiple announcements
    if (announcement_set_all := file_.announcement_set.all()) is not None:
        for announcement in announcement_set_all:
            announcement_branchs = announcement.branchs.all()

            # when announcement is for all branches
            if announcement_branchs.count() == 0:
                return response

            # when announcement is for specific branches
            if user_branch in announcement_branchs:
                return response

        raise PermissionDenied

    # impossible to reach here
    raise BadRequest
