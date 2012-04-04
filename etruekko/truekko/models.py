import os
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.db import models
from django.core.urlresolvers import reverse

from django.conf import settings

from djangoratings.fields import RatingField

from etruekko.utils import template_email


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
    rating = RatingField(range=5, can_change_vote=True)

    def int_rating(self):
        if self.rating.votes == 0:
            return self.rating.votes
        return int(self.rating.score / self.rating.votes)


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

    def members_emails(self):
        emails = [i.user.email for i in self.membership_set.all()]
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

# Transfer models

class Transfer(models.Model):
    user_from = models.ForeignKey(User, null=True, blank=True, related_name="transfer_from")
    group_from = models.ForeignKey(Group, null=True, blank=True, related_name="transfer_form")
    user_to = models.ForeignKey(User, related_name="transfer_to")
    concept = models.CharField(max_length=500)
    credits = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def type(self):
        return "transf"


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

# Service / items models

class Item(models.Model):
    TYPES = [
        ('IT', _('item')),
        ('SR', _('service')),
    ]

    PRICE_TYPES = [
        ('ETK', 'truekkos'),
        ('ETK/H', _('truekkos per hour')),
        ('ETK/KG', _('truekkos per kilogram')),
        ('ETK/L', _('truekkos per liter')),
        ('ETK/M', _('truekkos per metter')),
        ('ETK/M2', _('truekkos per square metter')),
        ('ETK/M3', _('truekkos per cubic metter')),
    ]

    user = models.ForeignKey(User, related_name="items")
    type = models.CharField(_("Item or service"), max_length=2, choices=TYPES, default="IT")
    demand = models.BooleanField(_("Demand"), default=False)
    name = models.CharField(_("Name"), max_length=150)
    description = models.TextField(_("Description"))
    price = models.IntegerField(_("Price"))
    price_type = models.CharField(_("Price type"), max_length=20, choices=PRICE_TYPES, default=PRICE_TYPES[0][0])
    photo = models.ImageField(_("photo"), blank=True, null=True,
                              upload_to=os.path.join(settings.MEDIA_ROOT,
                              "item_images"))
    pub_date = models.DateTimeField(auto_now_add=True)

    def tags(self):
        return (i.tag for i in self.itemtagged_set.all())

    def type_str(self):
        return 'item' if self.type == 'IT' else 'serv'

    def __unicode__(self):
        return "%s" % self.name


class Tag(models.Model):
    name = models.CharField(_("Name"), max_length=100)

    def __unicode__(self):
        return self.name


class ItemTagged(models.Model):
    item = models.ForeignKey(Item)
    tag = models.ForeignKey(Tag)

    def __unicode__(self):
        return "%s - %s" % (self.item.name, self.tag.name)


# Trasnf request

class Swap(models.Model):
    '''
    Related:
        * items
        * comments
    '''

    STATUS = [
        ('US1', _('User from confirmed')),
        ('US2', _('User to confirmed')),
        ('CON', _('confirmed')),
        ('DON', _('Done')),
        ('CAN', _('Cancel')),
    ]

    user_from = models.ForeignKey(User, related_name="swaps_from")
    user_to = models.ForeignKey(User, related_name="swaps_to")

    status = models.CharField(max_length=3, choices=STATUS)
    credits = models.IntegerField()
    date = models.DateTimeField(auto_now=True)

    def type(self):
        return "swap"

    def items_from(self):
        return [i.item for i in self.items.filter(item__user=self.user_from)]

    def items_to(self):
        return [i.item for i in self.items.filter(item__user=self.user_to)]


class SwapItems(models.Model):
    swap = models.ForeignKey(Swap, related_name="items")
    item = models.ForeignKey(Item)

class SwapComment(models.Model):
    swap = models.ForeignKey(Swap, related_name="comments")
    user = models.ForeignKey(User)
    comment = models.TextField()

def swap_post_save(sender, instance, created, *args, **kwargs):
    if instance.status == 'CON':
        p1 = instance.user_to.get_profile()
        p1.credits += instance.credits
        p1.save()

        p2 = instance.user_from.get_profile()
        p2.credits -= instance.credits
        p2.save()

        instance.status = 'DON'
        instance.save()

post_save.connect(swap_post_save, sender=Swap)


class Wall(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, related_name="walls")
    group = models.ForeignKey(Group, null=True, blank=True, related_name="walls")

    name = models.CharField(_("Name"), blank=True, null=True, max_length=100)
    description = models.TextField(_("Description"), max_length=300, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def messages_for_user(self, user):
        # TODO filter by group, membership and privacy
        return self.messages.all()

    def display_name(self):
        if self.user:
            return _("%s's wall") % self.user.username
        if self.group:
            return _("%s's wall") % self.group.name
        else:
            return self.name


class WallMessage(models.Model):
    user = models.ForeignKey(User, related_name="messages")
    wall = models.ForeignKey(Wall, related_name="messages")
    date = models.DateTimeField(auto_now_add=True)

    private = models.BooleanField(_("Private"), default=False)
    msg = models.TextField(_("Message"))

    def __unicode__(self):
        return self.msg

    class Meta:
        ordering = ['-date']

def wall_message_post_save(sender, instance, created, *args, **kwargs):
    if created:
        # Sending email notification to receiver
        if instance.wall.user:
            email_list = [instance.wall.user.email]
            url = reverse('view_profile', args=[instance.wall.user.username])
            name = instance.wall.user.get_profile().name
        elif instance.wall.group:
            email_list = instance.wall.group.members_emails()
            url = reverse('view_group', args=[instance.wall.group.name])
            name = instance.wall.group.name
        else:
            email_list = [i[1] for i in settings.ADMINS]
            url = '/'

        context = {'message': instance, 'name': name, 'url': url}
        template_email('truekko/message_mail.txt',
                       _("New message by %s in %s") % (instance.user, instance.wall.name),
                       email_list, context)

post_save.connect(wall_message_post_save, sender=WallMessage)
