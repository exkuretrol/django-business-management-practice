from typing import List, Literal, Optional

from ninja import NinjaAPI, Schema

from announcement.models import Announcement, StatusChoices
from checklist.models import Checklist

api = NinjaAPI(urls_namespace="api")


class AnnouncementActionSchema(Schema):
    announcements: List[str]
    action: Literal["edit", "unpublish", "publish", "delete", "archive"]


class ChecklistStatusSchema(Schema):
    checklist: str
    status: Literal["done", "todo"]


class MessageSchema(Schema):
    message: str


class Error(MessageSchema):
    code: str
    obj: Optional[str | int] = None
    obj_type: Optional[str] = None


class Success(MessageSchema):
    obj: Optional[str | int] = None


@api.post("/announcement/action", response={200: Success, 400: Error, 403: Error})
def announcement_action(request, data: AnnouncementActionSchema):
    user_group = request.user.groupuser_set.first().group
    if not request.user.is_superuser or not user_group.name == "總部":
        return 403, {
            "code": "permission_denied",
            "message": "Permission denied",
        }

    uuid_list = [announement for announement in data.announcements]

    if data.action in ["edit", "delete"]:
        return 400, {
            "code": "action_not_implemented",
            "message": "Action Not implemented yet.",
        }
    elif data.action in ["archive", "unpublish", "publish"]:
        if data.action == "archive":
            new_status = StatusChoices.UNAVAILABLE
        elif data.action == "unpublish":
            new_status = StatusChoices.DRAFT
        elif data.action == "publish":
            new_status = StatusChoices.PUBLISHED
        Announcement.objects.filter(uuid__in=uuid_list).update(status=new_status)

        return 200, {"message": "Updated successfully"}
    return 400, {"code": "action_invalid", "message": "Invalid action."}


@api.post("/checklist/status", response={200: Success, 400: Error, 403: Error})
def checklist_change_status(request, data: ChecklistStatusSchema):
    if data.status == "done":
        status = True
    elif data.status == "todo":
        status = False

    user_branch = request.user.member_set.first().org
    try:
        checklist = Checklist.objects.get(uuid=data.checklist)

        if checklist.branch != user_branch:
            return {
                "code": "permission_denied",
                "message": "Permission denied",
            }
        checklist.status = status
        checklist.last_modified_by = request.user
        checklist.save()
    except Checklist.DoesNotExist:
        return 400, {"code": "checklist_not_found", "message": "Checklist not found."}
    return 200, {"message": "Updated successfully"}
