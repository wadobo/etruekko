import os
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as _u
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.utils import simplejson

from django.conf import settings

from djangoratings.fields import RatingField

from etruekko.utils import template_email
from etruekko.globaltags.tags import avatar, groupavatar


# User profile models

class UserProfile(models.Model):
    '''
    User profile information
    '''

    user = models.ForeignKey(User)
    credits = models.IntegerField(default=0)
    name = models.CharField(_("Name"), blank=False, null=False,
                            default="Unnamed",
                            max_length=100)
    location = models.CharField(_("Location"), blank=False, null=False,
                                default="Unlocated",
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

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('view_profile', args=[self.user.username])

    def get_search_img(self):
        return avatar(self.user, 20)

    def get_search_desc(self):
        return '(%s) %s: %s' % (self.user.username, self.location, self.description)

    def is_admin_user(self, user):
        admin = self.user
        groups = Membership.objects.filter(role="ADM", user=admin).values('group')
        user_groups = Membership.objects.filter(role__in=["MEM", "REQ"],
                                                user=user,
                                                group__in=groups).count()
        if user_groups:
            return True

        return False

    def followers(self):
        return [i.follower for i in self.user.followers.all()]

    def followings(self):
        return [i.following for i in self.user.followings.all()]

    def valid_credits(self, value):
        min = settings.ETK_USER_MIN_CREDITS
        max = settings.ETK_USER_MAX_CREDITS
        return min <= self.credits + value <= max


class Follow(models.Model):
    '''
    Friendship relation, like in twitter
    '''

    follower = models.ForeignKey(User, related_name="followings")
    following = models.ForeignKey(User, related_name="followers")


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

    def get_absolute_url(self):
        return reverse('view_group', args=[self.id])

    def get_search_img(self):
        return groupavatar(self, 20)

    def get_search_desc(self):
        return '(%s) %s' % (self.location, self.description)

    def admins_emails(self):
        emails = [i.user.email for i in self.membership_set.filter(role="ADM")]
        return emails

    def members_emails(self):
        emails = [i.user.email for i in self.membership_set.all()]
        return emails

    def admins(self):
        return [i.user for i in self.membership_set.filter(role="ADM")]

    def is_admin(self, user):
        return bool(self.membership_set.filter(role="ADM", user=user).count())


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
    credits = models.PositiveIntegerField()
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

    OFFER = [
        ('OFF', _('Offer')),
        ('DEM', _('Demand')),
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
    offer_or_demand = models.CharField(_("Offer or demand"), max_length=3, choices=OFFER, default="OFF")
    name = models.CharField(_("Name"), max_length=150)
    description = models.TextField(_("Description"))
    price = models.IntegerField(_("Price"))
    price_type = models.CharField(_("Price type"), max_length=20, choices=PRICE_TYPES, default=PRICE_TYPES[0][0])
    photo = models.ImageField(_("photo"), blank=True, null=True,
                              upload_to=os.path.join(settings.MEDIA_ROOT,
                              "item_images"))
    pub_date = models.DateTimeField(auto_now_add=True)

    def demand(self):
        return self.offer_or_demand == "DEM"

    def get_absolute_url(self):
        return reverse('item_view', args=[self.id])

    def get_search_img(self):
        return avatar(self.user, 20)

    def get_search_desc(self):
        return '%s, %s: (%s) %s' % (self.get_type_display(),
                                    self.get_offer_or_demand_display(),
                                    self.user.get_profile().location,
                                    self.description)

    def tags(self):
        return (i.tag for i in self.itemtagged_set.all())

    def type_str(self):
        return 'item' if self.type == 'IT' else 'serv'

    def __unicode__(self):
        return "%s" % self.name

    class Meta:
        ordering = ['-pub_date']


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

    SWAP_MODE = [
        ('NON', _('---')),
        ('PER', _('In person')),
        ('MAI', _('Postal mail')),
        ('MSG', _('Express transport')),
    ]

    user_from = models.ForeignKey(User, related_name="swaps_from")
    user_to = models.ForeignKey(User, related_name="swaps_to")

    status = models.CharField(max_length=3, choices=STATUS)
    swap_mode = models.CharField(max_length=3, choices=SWAP_MODE, default="NON")
    credits_from = models.PositiveIntegerField(default=0)
    credits_to = models.PositiveIntegerField(default=0)
    done_msg = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def type(self):
        return "swap"

    def finished(self):
        return self.status in ['DON', 'CAN']

    def get_status_msg(self):
        if self.status == 'US1':
            u = self.user_to.username
            return _("Negotiation, waiting for %s confirmation") % u
        elif self.status == 'US2':
            u = self.user_from.username
            return _("Negotiation, waiting for %s confirmation") % u
        elif self.status == 'CON':
            return _("Swap confirmed")
        elif self.status == 'DON':
            return _("Swap done")
        elif self.status == 'CAN':
            return _("Swap canceled")

    def items_from_names(self):
        if self.done_msg:
            items = simplejson.loads(self.done_msg)
            return items['from']

        return [i.item.name for i in self.items.filter(item__user=self.user_from)]

    def items_to_names(self):
        if self.done_msg:
            items = simplejson.loads(self.done_msg)
            return items['to']

        return [i.item.name for i in self.items.filter(item__user=self.user_to)]

    def items_from(self):
        return [i.item for i in self.items.filter(item__user=self.user_from)]

    def items_to(self):
        return [i.item for i in self.items.filter(item__user=self.user_to)]

    def is_valid(self):
        p1 = self.user_from.get_profile()
        p2 = self.user_to.get_profile()
        try:
            c1 = abs(int(self.credits_from))
            c2 = abs(int(self.credits_to))
            self.credits_from = c1
            self.credits_to = c2
        except:
            return False
        return p1.valid_credits(c2 - c1) and p2.valid_credits(c1 - c2)


class SwapItems(models.Model):
    swap = models.ForeignKey(Swap, related_name="items")
    item = models.ForeignKey(Item)

class SwapComment(models.Model):
    swap = models.ForeignKey(Swap, related_name="comments")
    user = models.ForeignKey(User)
    comment = models.TextField()

def swap_post_save(sender, instance, created, *args, **kwargs):
    if created:
        return

    # last comment
    comment = ''
    last_comment = ''
    c = instance.comments.all().order_by("-id")
    if c.count():
        last_comment = c[0].comment

    if instance.status == 'CON':
        p1 = instance.user_to.get_profile()
        p1.credits += instance.credits_from
        p1.credits -= instance.credits_to
        p1.save()

        p2 = instance.user_from.get_profile()
        p2.credits += instance.credits_to
        p2.credits -= instance.credits_from
        p2.save()

        instance.status = 'DON'
        items = {'from': [i.name for i in instance.items_from()], 'to': [i.name for i in instance.items_to()]}
        instance.done_msg = simplejson.dumps(items)
        instance.save()
        return

    elif instance.status == 'DON':
        comment = _u("Conglatulations, swap has been accepted")
        title = _u("A swap has been accepted")
    elif instance.status in ['US1', 'US2']:
        title = _u("A swap has been modified")
    elif instance.status == 'CAN':
        title = _u("A swap has been canceled")

    url = reverse('swap_view', args=(instance.id,))

    context = {'swap': instance, 'url': url, 'comment': comment,
               'last_comment': last_comment,
               'credit_name': settings.ETK_CREDIT,
               'status': instance.get_status_msg()}
    template_email('truekko/swap_modified_mail.txt',
                   title,
                   [instance.user_to.email, instance.user_from.email], context)

post_save.connect(swap_post_save, sender=Swap)


class Wall(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, related_name="walls")
    group = models.ForeignKey(Group, null=True, blank=True, related_name="walls")

    name = models.CharField(_("Name"), blank=True, null=True, max_length=100)
    description = models.TextField(_("Description"), max_length=300, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def messages_for_user(self, user):
        from etruekko.truekko.decorators import is_member
        query = Q(parent=None)

        if user.is_anonymous():
            query = query & Q(private=False)
            return self.messages.filter(query)
        # replies will be shown in template

        if self.user:
            if self.user == user:
                return self.messages.filter(query)
            else:
                query = query & (Q(private=False) | Q(user=user))
                return self.messages.filter(query)

        if self.group:
            if is_member(user, self.group):
                return self.messages.filter(query)
            else:
                query = query & (Q(private=False) | Q(user=user))
                return self.messages.filter(query)

        return self.messages.filter(query)


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
    parent = models.ForeignKey("WallMessage", related_name="childs", null=True)
    date = models.DateTimeField(auto_now_add=True)

    private = models.BooleanField(_("Private"), default=False)
    msg = models.TextField(_("Message"))

    def get_childs(self):
        return self.childs.all().order_by("date")

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
            url = reverse('view_group', args=[instance.wall.group.id])
            name = instance.wall.group.name
        else:
            email_list = [i[1] for i in settings.ADMINS]
            url = '/'

        context = {'message': instance, 'name': name, 'url': url}
        template_email('truekko/message_mail.txt',
                       _("New message by %(user)s in %(wall)s") % dict(user=instance.user, wall=instance.wall.name),
                       email_list, context)

post_save.connect(wall_message_post_save, sender=WallMessage)


class Denounce(models.Model):
    STATUS = [
        ('PEN', _('pending')),
        ('CON', _('confirmed')),
        ('RES', _('resolved')),
        ('CAN', _('cancel')),
    ]

    user_from = models.ForeignKey(User, related_name="dennounces_from")
    user_to = models.ForeignKey(User, related_name="dennounces_to")
    group = models.ForeignKey(Group)
    date = models.DateTimeField(auto_now=True)

    msg = models.TextField(_("Message"))
    status = models.CharField(max_length=3, choices=STATUS, default='PEN')

    def __unicode__(self):
        return "%s - %s" % (self.user_from.username, self.user_to.username)

    class Meta:
        ordering = ['-date']

def denounce_post_save(sender, instance, created, *args, **kwargs):
    if created:
        # Sending email notification to admin, denouncer and denounced
        email_list = instance.group.admins_emails() + [instance.user_from.email, instance.user_to.email]
        url = reverse('group_denounce_view', args=[instance.id])

        context = {'denounce': instance, 'url': url}
        template_email('truekko/denounce_mail.txt',
                       _("%(user)s user has been denounced in group %(group)s") % dict(user=instance.user_to.username, group=instance.group.name),
                       email_list, context)

post_save.connect(denounce_post_save, sender=Denounce)
