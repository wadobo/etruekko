from django.conf.urls.defaults import *

urlpatterns = patterns('etruekko.truekko.views',
    url(r'^profile/edit$', 'edit_profile', name='edit_profile'),
    url(r'^profile/edit/(\w+)$', 'edit_profile_admin', name='edit_profile_admin'),
    url(r'^profile/postal$', 'edit_postal', name='edit_postal'),
    url(r'^profile/postal/(\w+)$', 'edit_postal', name='edit_postal'),
    url(r'^profile/(\w+)$', 'view_profile', name='view_profile'),
    url(r'^people/(\w+)?$', 'people', name='people'),
    url(r'^rate/(\d+)$', 'rate_user', name='rate_user'),
    # follow
    url(r'^follow/(\d+)$', 'follow', name='follow'),
    url(r'^unfollow/(\d+)$', 'unfollow', name='unfollow'),
    url(r'^follow/(\d+)(\.json)$', 'follow', name='follow-json'),
    url(r'^unfollow/(\d+)(\.json)$', 'unfollow', name='unfollow-json'),

    url(r'^followings/(\d+)?$', 'followings', name='followings'),
    url(r'^followers/(\d+)?$', 'followers', name='followers'),
    # channels
    url(r'^channel/view/(\d+)$', 'channel_view', name='channel_view'),
    # communities (old groups)
    url(r'^communities$', 'groups', name='groups'),
    url(r'^communities/all$', 'groups_all', name='groups_all'),
    url(r'^community/(\d+)$', 'view_group', name='view_group'),
    url(r'^community/edit/(\d+)$', 'edit_group', name='edit_group'),
    url(r'^community/edit/members/(\d+)$', 'edit_group_members', name='edit_group_members'),
    url(r'^community/memberlist/(\d+)$', 'group_member_list', name='member_list'),
    url(r'^community/join/(\d+)$', 'join_group', name='join_group'),
    url(r'^community/leave/(\d+)$', 'leave_group', name='leave_group'),
    url(r'^community/register/(\d+)$', 'register_group', name='register_group'),
    url(r'^community/admin/register/(\d+)$', 'register_group_admin', name='register_group_admin'),
    url(r'^community/register/confirm/(\d+)$', 'register_confirm', name='register_confirm'),
    url(r'^community/denounce/(\d+)$', 'group_denounce', name='group_denounce'),
    url(r'^community/denounce/(\d+)/(\w+)$', 'group_denounce_user', name='group_denounce_user'),
    url(r'^community/denounce/view/(\d+)$', 'group_denounce_view', name='group_denounce_view'),
    # register
    url(r'^register$', 'register_wizard', name='register_wizard'),
    # transfer
    url(r'^transfer/direct/(\w+)$', 'transfer_direct', name='transfer_direct'),
    url(r'^transfer/list$', 'transfer_list', name='transfer_list'),
    # swap
    url(r'^swap/list$', 'swap_list', name='swap_list'),
    url(r'^swap/view/(\d+)$', 'swap_view', name='swap_view'),
    url(r'^swap/(\w+)$', 'swap_creation', name='swap_creation'),
    url(r'^commitment/create/(\d+)$', 'commitment_create', name='commitment_create'),
    url(r'^commitment/done/(\d+)$', 'commitment_done', name='commitment_done'),
    url(r'^commitment/delete/(\d+)$', 'commitment_delete', name='commitment_delete'),
    # item
    url(r'^item/add$', 'item_add', name='item_add'),
    url(r'^item/edit/(?P<object_id>\d+)$', 'item_add', name='item_edit'),
    url(r'^item/remove/(\d+)$', 'item_remove', name='item_remove'),
    url(r'^item/view/(\d+)/?$', 'item_view', name='item_view'),
    url(r'^item/list/(item|serv)/(\w+)?$', 'item_list', name='item_list'),
    # messages
    url(r'^messages/post/(\d+)$', 'message_post', name='message_post'),
    url(r'^messages/remove/(\d+)$', 'message_remove', name='message_remove'),
    # search
    url(r'^search/advanced$', 'search_advanced', name='search_advanced'),
    url(r'^search/', include('haystack.urls')),
    # etruekko
    url(r'^etruekko$', 'etruekko', name='etruekko'),
    # contact
    url(r'^contact$', 'contact', name='contact'),
    url(r'^contact/community$', 'new_community_contact', name='new_community_contact'),
    url(r'^contact/ad$', 'new_ad_contact', name='new_ad_contact'),
    # faq
    url(r'^faq$', 'faq', name='faq'),
    url(r'^terms$', 'terms', name='terms'),
    url(r'^privacy$', 'privacy', name='privacy'),

    url(r'^$', 'index', name='index'),
)
