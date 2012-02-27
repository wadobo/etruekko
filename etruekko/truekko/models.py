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
    if new:
        profile.credits += settings.ETK_USER_INITIAL_CREDITS
        profile.save()


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

    # TODO add here membership conditions

    def __unicode__(self):
        return self.name

    def admins_emails(self):
        emails = [i.user.email for i in self.membership_set.filter(role="ADM")]
        return emails


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


class Transfer(models.Model):
    user_from = models.ForeignKey(User, null=True, blank=True, related_name="transfer_from")
    group_from = models.ForeignKey(Group, null=True, blank=True, related_name="transfer_form")
    user_to = models.ForeignKey(User, related_name="transfer_to")
    concept = models.CharField(max_length=500)
    credits = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)


def transfer_post_save(sender, instance, created, *args, **kwargs):
    if created:
        p1 = instance.user_to.get_profile()
        p1.credits += instance.credits
        p1.save()

        if instance.user_from:
            p2 = instance.user_from.get_profile()
            p2.credits -= instance.credits
            p2.save()
        else:
            instance.group_from.credits -= instance.credits
            instance.group_from.save()


post_save.connect(transfer_post_save, sender=Transfer)
