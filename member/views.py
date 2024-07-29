import datetime

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string


def login_view(request):
    from django.contrib.auth import authenticate, login

    context = {}
    next_url = request.GET.get("next", "")
    if request.user.is_authenticated:
        return HttpResponseRedirect("/")

    if request.method == "POST":
        empid = request.POST.get("empid", "")
        password = request.POST.get("password", "")
        context["empid"] = empid
        context["password"] = password

        if empid == "" or password == "":
            context["err_msg"] = "帳號密碼不得為空"
            return render(request, "login.html", context)
        else:
            from member.models import Member

            member = Member.objects.filter(employee_id=empid)
            if member.count() > 0:
                member = member[0]
            else:
                context["err_msg"] = "沒有此帳號的使用者"
                return render(request, "login.html", context)

            login_user = authenticate(username=member.user.username, password=password)
            if login_user is not None:
                if login_user.is_active:
                    login(request, login_user)
                    context["success"] = True
                    context["next"] = next_url
                    if next_url == "":
                        return HttpResponseRedirect("/")
                    else:
                        return HttpResponseRedirect(next_url)
                else:
                    context["err_msg"] = "該帳號暫停使用中,請洽系統人員!"
            else:
                context["err_msg"] = "帳號/密碼錯誤"

    return render(request, "login.html", context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/login/")


@login_required
def index_view(request):
    c = {}
    from member.models import Member

    member = Member.objects.filter(user=request.user)
    if member.count() > 0:
        member = member[0]
    else:
        raise Exception("無對應的Member資料")

    if member.password_changetime == "":
        return HttpResponseRedirect("/member/password/change/?mid=%s" % member.uuid)

    c["member"] = member

    return render(request, "index.html", c)


@login_required
def account_list_view(request):
    context = {}
    template = "member/account_list.html"
    from member.models import Member

    member = Member.objects.filter(user=request.user)
    if member.count() > 0:
        member = member[0]
        context["member"] = member
    else:
        raise Exception("無對應的Member資料")

    members = Member.objects.all()
    context["members"] = members
    html = render_to_string(template, context, request=request)

    return HttpResponse(html)


@login_required
def account_create_view(request):
    context = {}
    template = "member/account_create.html"
    from django.contrib.auth.models import User

    from member.models import AccessGroup, GroupUser, Member, Organization

    member = Member.objects.filter(user=request.user)
    if member.count() > 0:
        member = member[0]
        context["member"] = member
    else:
        raise Exception("無對應的Member資料")

    orgs = Organization.objects.all()
    context["orgs"] = orgs

    access_groups = AccessGroup.objects.all()
    context["access_groups"] = access_groups

    if request.method == "POST":
        employee_id = request.POST.get("employee_id", "")
        first_name = request.POST.get("first_name", "")
        org_uuid = request.POST.get("org", "")
        department = request.POST.get("department", "")
        unit = request.POST.get("unit", "")
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        ag_uuid = request.POST.get("access_group", "")
        context["employee_id"] = employee_id
        context["first_name"] = first_name
        context["org_uuid"] = org_uuid
        context["password"] = password
        context["password2"] = password2
        context["ag_uuid"] = ag_uuid
        context["department"] = department
        context["unit"] = unit

        if (
            employee_id == ""
            or first_name == ""
            or org_uuid == ""
            or password == ""
            or password2 == ""
            or ag_uuid == ""
            or department == ""
            or unit == ""
        ):
            context["err_msg"] = "請輸入必要欄位"
            html = render_to_string(template, context, request=request)
            return HttpResponse(html)

        if password != password2:
            context["err_msg"] = "再輸入密碼與密碼不同"
            html = render_to_string(template, context, request=request)
            return HttpResponse(html)

        check_member = Member.objects.filter(employee_id=employee_id).count()
        check_user = User.objects.filter(username=employee_id).count()
        if check_member > 0 or check_user > 0:
            context["err_msg"] = "員工編號已使用"
            html = render_to_string(template, context, request=request)
            return HttpResponse(html)

        try:
            org = Organization.objects.get(uuid=org_uuid)
            context["org"] = org
        except:
            context["err_msg"] = "錯誤的單位"
            html = render_to_string(template, context, request=request)
            return HttpResponse(html)

        try:
            ag = AccessGroup.objects.get(uuid=ag_uuid)
            context["ag"] = ag
        except:
            context["err_msg"] = "錯誤的群組"
            html = render_to_string(template, context, request=request)
            return HttpResponse(html)

        try:
            new_user = User.objects.create_user(username=employee_id)
            new_user.first_name = first_name
            new_user.set_password(password)
            new_user.save()
        except:
            context["err_msg"] = "帳號建立失敗"
            html = render_to_string(template, context, request=request)
            return HttpResponse(html)

        now = datetime.datetime.now()

        new_member = Member()
        new_member.user = new_user
        new_member.employee_id = employee_id
        new_member.org = org
        new_member.department = department
        new_member.unit = unit
        new_member.password_hash = new_user.password
        new_member.password_changetime = ""
        new_member.save()

        # To-Do:設定群組
        gu = GroupUser()
        gu.group = ag
        gu.user = new_user
        gu.save()

        return HttpResponseRedirect("/member/account/create/success/")

    html = render_to_string(template, context, request=request)
    return HttpResponse(html)


@login_required
def account_create_success_view(request):
    context = {}
    template = "member/account_create_success.html"
    from member.models import Member

    member = Member.objects.filter(user=request.user)
    if member.count() > 0:
        member = member[0]
        context["member"] = member
    else:
        raise Exception("無對應的Member資料")

    html = render_to_string(template, context, request=request)

    return HttpResponse(html)


@login_required
def account_edit_view(request):
    context = {}
    template = "member/account_edit.html"
    from django.contrib.auth.models import User

    from member.models import AccessGroup, GroupUser, Member, Organization

    member = Member.objects.filter(user=request.user)
    if member.count() > 0:
        member = member[0]
        context["member"] = member
    else:
        raise Exception("無對應的Member資料")

    orgs = Organization.objects.all()
    context["orgs"] = orgs

    access_groups = AccessGroup.objects.all()
    context["access_groups"] = access_groups

    mid = request.GET.get("mid", "")
    try:
        tm = Member.objects.get(uuid=mid)
        context["tm"] = tm
    except:
        context["err_msg"] = "錯誤的參數"
        html = render_to_string(template, context, request=request)
        return HttpResponse(html)

    if request.method == "POST":
        employee_id = request.POST.get("employee_id", "")
        first_name = request.POST.get("first_name", "")
        org_uuid = request.POST.get("org", "")
        department = request.POST.get("department", "")
        unit = request.POST.get("unit", "")
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        ag_uuid = request.POST.get("access_group", "")
        context["employee_id"] = employee_id
        context["first_name"] = first_name
        context["org_uuid"] = org_uuid
        context["password"] = password
        context["password2"] = password2
        context["ag_uuid"] = ag_uuid
        context["department"] = department
        context["unit"] = unit

        if (
            employee_id == ""
            or first_name == ""
            or org_uuid == ""
            or ag_uuid == ""
            or department == ""
            or unit == ""
        ):
            context["err_msg"] = "請輸入必要欄位"
            html = render_to_string(template, context, request=request)
            return HttpResponse(html)

        check_member = (
            Member.objects.filter(employee_id=employee_id).exclude(user=tm.user).count()
        )
        if check_member > 0:
            context["err_msg"] = "員工編號已使用"
            html = render_to_string(template, context, request=request)
            return HttpResponse(html)

        try:
            org = Organization.objects.get(uuid=org_uuid)
            context["org"] = org
        except:
            context["err_msg"] = "錯誤的單位"
            html = render_to_string(template, context, request=request)
            return HttpResponse(html)

        try:
            ag = AccessGroup.objects.get(uuid=ag_uuid)
            context["ag"] = ag
        except:
            context["err_msg"] = "錯誤的群組"
            html = render_to_string(template, context, request=request)
            return HttpResponse(html)

        tu = tm.user
        tu.first_name = first_name
        if password != "":
            new_user.set_password(password)
        tu.save()

        now = datetime.datetime.now()
        tm.employee_id = employee_id
        tm.org = org
        tm.department = department
        tm.unit = unit
        if password != "":
            tm.password_hash = new_user.password
            tm.password_changetime = ""

        tm.save()

        check_group = GroupUser.objects.filter(group=ag, user=tu).count()
        if check_group == 0:  # 要變更群組
            GroupUser.objects.filter(user=tu).delete()
            gu = GroupUser()
            gu.group = ag
            gu.user = new_user
            gu.save()
        return HttpResponseRedirect("/member/account/edit/success/")
    else:
        context["tm"] = tm

    html = render_to_string(template, context, request=request)
    return HttpResponse(html)


@login_required
def account_edit_success_view(request):
    context = {}
    template = "member/account_edit_success.html"
    from member.models import Member

    member = Member.objects.filter(user=request.user)
    if member.count() > 0:
        member = member[0]
    else:
        raise Exception("無對應的Member資料")

    html = render_to_string(template, context, request=request)

    return HttpResponse(html)


@login_required
def account_delete_view(request):
    context = {}
    template = "member/account_delete.html"
    from django.contrib.auth.models import User

    from member.models import AccessGroup, GroupUser, Member, Unit

    member = Member.objects.filter(user=request.user)
    if member.count() > 0:
        member = member[0]
        context["member"] = member
    else:
        raise Exception("無對應的Member資料")

    if request.method == "POST":
        mid = request.POST.get("mid", "")
        try:
            mid = int(mid)
            tm = Member.objects.get(id=mid)
            context["tm"] = tm
        except:
            context["err_msg"] = "錯誤的參數或資料不存在"
            html = render_to_string(template, context, request=request)
            return HttpResponse(html)

        tu = tm.user
        tu.delete()
        context["success"] = True

    else:
        return HttpResponseRedirect("/member/account/")

    html = render_to_string(template, context, request=request)
    return HttpResponse(html)


@login_required
def password_change_view(request):
    context = {}
    template = "member/password_change.html"
    from django.contrib.auth.models import User

    from member.models import AccessGroup, GroupUser, Member, Organization

    member = Member.objects.filter(user=request.user)
    if member.count() > 0:
        member = member[0]
        context["member"] = member
    else:
        raise Exception("無對應的Member資料")

    mid = request.GET.get("mid", "")
    try:
        tm = Member.objects.get(uuid=mid)
        context["tm"] = tm
    except:
        context["err_msg"] = "錯誤的參數"
        html = render_to_string(template, context, request=request)
        return HttpResponse(html)

    if request.method == "POST":
        tu = tm.user

        old_password = request.POST.get("old_password", "")
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")

        if password == "" or password2 == "":
            context["err_msg"] = "請輸入必要欄位"
            html = render_to_string(template, context, request=request)
            return HttpResponse(html)

        if password != password2:
            context["err_msg"] = "再輸入密碼與密碼不同"
            html = render_to_string(template, context, request=request)
            return HttpResponse(html)

        if tu == request.user and old_password == "":
            context["err_msg"] = "請輸入現有密碼"
            html = render_to_string(template, context, request=request)
            return HttpResponse(html)

        from django.contrib.auth.hashers import check_password

        if tu == request.user:  # 自行變更密碼要驗證, 管理者不用
            if not check_password(old_password, tu.password):
                context["err_msg"] = "現有密碼錯誤"
                html = render_to_string(template, context, request=request)
                return HttpResponse(html)

            if (
                check_password(password, tm.password_hash)
                or check_password(password, tm.password_hash2)
                or check_password(password, tm.password_hash3)
            ):
                context["err_msg"] = "新密碼不可以與前三次密碼相同"
                html = render_to_string(template, context, request=request)
                return HttpResponse(html)

        tu.set_password(password)
        tu.save()

        if tu == request.user:  # 自行變更密碼需要紀錄, 管理者修改不紀錄
            now = datetime.datetime.now()
            tm.password_hash3 = tm.password_hash2
            tm.password_changetime3 = tm.password_changetime2
            tm.password_hash2 = tm.password_hash
            tm.password_changetime2 = tm.password_changetime
            tm.password_hash = tu.password
            tm.password_changetime = now.strftime("%Y-%m-%d %H:%M:%S")
            tm.save()

        return HttpResponseRedirect("/member/password/change/success/")
    else:
        context["tm"] = tm

    html = render_to_string(template, context, request=request)
    return HttpResponse(html)


def password_change_success_view(request):
    context = {}
    if request.user.is_authenticated:
        template = "member/password_change_success.html"
        from member.models import Member

        member = Member.objects.filter(user=request.user)
        if member.count() > 0:
            member = member[0]
        else:
            raise Exception("無對應的Member資料")
    else:
        template = "member/password_change_success_relogin.html"

    html = render_to_string(template, context, request=request)

    return HttpResponse(html)
