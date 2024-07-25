from dal import autocomplete
from django.contrib.auth.views import LoginView
from django.http import FileResponse, HttpRequest, JsonResponse
from django.views.generic import TemplateView

from .forms import FileUploadForm, LoginForm
from .models import File


class NewLoginView(LoginView):
    form_class = LoginForm


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
    file_ = File.objects.get(id=file_id)
    return FileResponse(file_.file, as_attachment=True, filename=file_.name)
