from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('truekko.views',
    (r'^$', direct_to_template, {'template': 'truekko/index.html',
                                 'extra_context': {'klass': 'home'}}),
)
