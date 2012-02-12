import os
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.db import models

from django.conf import settings


# User profile models

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
    web = models.URLField(_("Web"), blank=True, null=True, default="")
    photo = models.ImageField(_("Avatar"), blank=True, null=True,
                              upload_to=os.path.join(settings.MEDIA_ROOT, "photos"))
    description = models.TextField(_("Personal description"), max_length=300,
                                   blank=True)


def user_post_save(sender, instance, signal, *args, **kwargs):
    profile, new = UserProfile.objects.get_or_create(user=instance)


post_save.connect(user_post_save, sender=User)


# Groups models

class Group(models.Model):
    '''
    Model that represents a barter group.
    '''

    name = models.CharField(_("Name"), max_length=500, unique=True)
    email = models.EmailField(_("Email"))
    location = models.CharField(_("Location"), blank=True, null=True,
                                max_length=100)
    web = models.URLField(_("Web"), blank=True, null=True, default="")
    photo = models.ImageField(_("Avatar"), blank=True, null=True,
                              upload_to=os.path.join(settings.MEDIA_ROOT, "photos"))
    description = models.TextField(_("Group description"), max_length=800,
                                   blank=True)

    def __unicode__(self):
        return self.name

    # TODO add here membership conditions


class Membership(models.Model):
    '''
    Group -- User membership relation

    An user could be member of severals groups and a group could have
    more than one user

    the role is how the user is related with the group
    '''

    ROLES = [('ADM', 'admin'),
             ('MEM', 'member'),
             ('REQ', 'requester'),
             ('BAN', 'banned'),
             ]

    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    role = models.CharField(choices=ROLES, max_length=3)

    def __unicode__(self):
        return "%s - %s - %s" % (self.user.username, self.group.name, self.role)
