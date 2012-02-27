from django.contrib import admin
from truekko.models import UserProfile, Group, Membership
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


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'credits', 'location')


admin.site.register(Group, GroupAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
