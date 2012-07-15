from django.contrib import admin
from etruekko.truekko.models import UserProfile, Group, Membership
from etruekko.truekko.models import Item, Tag, ItemTagged
from etruekko.truekko.models import Channel
from etruekko.truekko.models import Ad
from django.db import models


class MembershipInline(admin.TabularInline):
    model = Membership
    fk_name = "group"


class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


class GroupAdmin(admin.ModelAdmin):
    inlines = [
        MembershipInline,
    ]
    list_display = ('name', 'location', 'email', 'web', 'description')


class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role')


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'credits', 'location')


class TagInline(admin.TabularInline):
    model = ItemTagged
    fk_name = "item"


class ItemAdmin(admin.ModelAdmin):
    inlines = [
        TagInline,
    ]
    list_display = ('user', 'name', 'type', 'description', 'price', 'price_type')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ItemTaggedAdmin(admin.ModelAdmin):
    list_display = ('item', 'tag')


class AdAdmin(admin.ModelAdmin):
    list_display = ('info', 'active', 'position', 'type', 'priority')


admin.site.register(Channel, ChannelAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

admin.site.register(Item, ItemAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ItemTagged, ItemTaggedAdmin)

admin.site.register(Ad, AdAdmin)
