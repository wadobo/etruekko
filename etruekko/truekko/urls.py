from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('truekko.views',
    url(r'^profile/edit$', 'edit_profile', name='edit_profile'),
    url(r'^profile/(\w+)$', 'view_profile', name='view_profile'),
    url(r'^people$', 'people', name='people'),
    # groups
    url(r'^groups$', 'groups', name='groups'),
    url(r'^group/(\w+)$', 'view_group', name='view_group'),
    url(r'^group/edit/(\w+)$', 'edit_group', name='edit_group'),
    url(r'^group/edit/members/(\w+)$', 'edit_group_members', name='edit_group_members'),
    url(r'^group/join/(\w+)$', 'join_group', name='join_group'),
    url(r'^group/leave/(\w+)$', 'leave_group', name='leave_group'),
    url(r'^group/register/(\w+)$', 'register_group', name='register_group'),
    url(r'^group/admin/register/(\w+)$', 'register_group_admin', name='register_group_admin'),
    url(r'^group/register/confirm/(\w+)$', 'register_confirm', name='register_confirm'),
    # transfer
    url(r'^transfer/direct/(\w+)$', 'transfer_direct', name='transfer_direct'),
    url(r'^transfer/list$', 'transfer_list', name='transfer_list'),

    url(r'^$', 'index', name='index'),
)
