from django.contrib import admin
from truekko.models import Group, Membership
from django.db import models


class MembershipInline(admin.TabularInline):
    model = Membership
    fk_name = "group"


class GroupAdmin(admin.ModelAdmin):
    inlines = [
        MembershipInline,
    ]
    list_display = ('name', 'location', 'email', 'web', 'description')


class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role')


admin.site.register(Group, GroupAdmin)
admin.site.register(Membership, MembershipAdmin)
