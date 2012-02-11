from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('truekko.views',
    url(r'^profile/edit$', 'edit_profile', name='edit_profile'),
    url(r'^profile/(\w+)$', 'view_profile', name='view_profile'),
    url(r'^people$', 'people', name='people'),
    url(r'^groups$', 'groups', name='groups'),
    url(r'^group/(\w+)$', 'view_group', name='view_group'),
    url(r'^group/edit/(\w+)$', 'edit_group', name='edit_group'),
    url(r'^$', 'index', name='index'),
)
