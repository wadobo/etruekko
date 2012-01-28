import os
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.db import models

from django.conf import settings


class UserProfile(models.Model):
    '''
    User profile information
    '''

    user = models.ForeignKey(User)
    credits = models.IntegerField(default=0)
    name = models.CharField(_("Name"), blank=True, null=True,
                            max_length=100)
    location = models.CharField(_("Location"), blank=True, null=True,
                                max_length=100)
    web = models.URLField(_("Web"), blank=True, null=True)
    photo = models.ImageField(_("Avatar"), blank=True, null=True,
                              upload_to=os.path.join(settings.MEDIA_ROOT, "photos"))
    description = models.TextField(_("Personal description"), max_length=300,
                                   blank=True)


def user_post_save(sender, instance, signal, *args, **kwargs):
    profile, new = UserProfile.objects.get_or_create(user=instance)


post_save.connect(user_post_save, sender=User)
