from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', include('truekko.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name="login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name="logout"),

)

if settings.DEBUG:
    urlpatterns += patterns('',
                    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                      {'document_root': settings.MEDIA_ROOT}), )
