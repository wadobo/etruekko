from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('truekko.views',
    url(r'^profile/edit$', 'edit_profile', name='edit_profile'),
    url(r'^profile/(\w+)$', 'view_profile', name='view_profile'),
    url(r'^people$', 'people', name='people'),
    url(r'^$', 'index', name='index'),
)
