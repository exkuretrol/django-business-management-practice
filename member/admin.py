from django import forms
from django.contrib import admin

from member.models import Member


class MemberAdminForm(forms.ModelForm):
    class Meta:
        model = Member
        exclude = []


class MemberAdmin(admin.ModelAdmin):
    search_fields = ["user__email", "user__first_name", "mobile"]

    # class Media:
    #    js = ('/media/js/tiny_mce/tiny_mce.js','/media/admin/js/calendar.js', '/media/admin/js/admin/DateTimeShortcuts.js')
    form = MemberAdminForm


admin.site.register(Member, MemberAdmin)


from member.models import Organization


class OrganizationAdminForm(forms.ModelForm):
    class Meta:
        model = Organization
        exclude = []


class OrganizationAdmin(admin.ModelAdmin):
    search_fields = ["name", "create_datetime", "update_datetime"]

    # class Media:
    #    js = ('/media/js/tiny_mce/tiny_mce.js','/media/admin/js/calendar.js', '/media/admin/js/admin/DateTimeShortcuts.js')
    form = OrganizationAdminForm


admin.site.register(Organization, OrganizationAdmin)


from member.models import AccessGroup


class AccessGroupAdminForm(forms.ModelForm):
    class Meta:
        model = AccessGroup
        exclude = []


class AccessGroupAdmin(admin.ModelAdmin):
    search_fields = ["name", "create_datetime", "update_datetime"]

    # class Media:
    #    js = ('/media/js/tiny_mce/tiny_mce.js','/media/admin/js/calendar.js', '/media/admin/js/admin/DateTimeShortcuts.js')
    form = AccessGroupAdminForm


admin.site.register(AccessGroup, AccessGroupAdmin)
