from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import views as auth_views
from etruekko.truekko.views import PasswordResetDoneView
from etruekko.truekko.views import PasswordResetCompleteView

from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'', include('etruekko.truekko.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name="login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name="logout"),

    # Reset password
    url(r'^password/reset/$',
       auth_views.password_reset,
       {'template_name': 'accounts/password_reset.html',
        'email_template_name': 'accounts/emails/password_reset_message.txt',
        'post_reset_redirect': reverse_lazy('password_reset_done'),
        'extra_context': {'title': _('Reset password')},
        },
       name='password_reset'),

    url(r'^password/reset/done/$',
       PasswordResetDoneView.as_view(),
       name='password_reset_done'),

    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
       auth_views.password_reset_confirm,
       {'template_name': 'accounts/password_reset_confirm_form.html',
        'post_reset_redirect': reverse_lazy('password_reset_complete'),
        'extra_context': {'title': _('Reset password')},
       },
       name='password_reset_confirm'),

    url(r'^password/reset/confirm/complete/$',
       PasswordResetCompleteView.as_view(),
       name='password_reset_complete'),

    # Change password
    url(r'password/change/$',
        auth_views.password_change,
        {'template_name': 'accounts/password_reset.html',
         'post_change_redirect': reverse_lazy('edit_profile'),
         'extra_context': {'title': _('Change password')},
        },
        name='password_change'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
                    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                      {'document_root': settings.MEDIA_ROOT}), )
