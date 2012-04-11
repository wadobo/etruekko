import uuid

from django.http import Http404
from django.contrib import messages
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import View, TemplateView
from django.contrib.auth.decorators import login_required
from decorators import is_group_admin, is_group_editable, is_member
from django.shortcuts import render_to_response
from django.db.models import Q

from etruekko.truekko.forms import UserProfileForm
from etruekko.truekko.forms import GroupForm
from etruekko.truekko.forms import RegisterForm
from etruekko.truekko.forms import TransferDirectForm
from etruekko.truekko.forms import ItemAddForm

from etruekko.truekko.models import UserProfile
from etruekko.truekko.models import User
from etruekko.truekko.models import Group
from etruekko.truekko.models import Membership
from etruekko.truekko.models import Transfer
from etruekko.truekko.models import Item
from etruekko.truekko.models import Tag
from etruekko.truekko.models import ItemTagged
from etruekko.truekko.models import Swap, SwapItems, SwapComment
from etruekko.truekko.models import Wall, WallMessage

from etruekko.truekko.utils import generate_menu
from etruekko.utils import paginate, template_email


class Index(TemplateView):
    template_name = 'truekko/index.html'

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['klass'] = 'home'
        context['menu'] = generate_menu("home")

        if self.request.user.is_authenticated():
            u = self.request.user
            groups = [i.group for i in Membership.objects.filter(user=u)]
            wall, created = Wall.objects.get_or_create(user=u, name="%s wall" % u.username)
            messages = self.messages_for_user()
            context['wallmessages'] = paginate(self.request, messages, 20)
            context['wall'] = wall
            context['groups'] = groups
            items = Item.objects.filter(user=u)
            context['offers'] = items.filter(demand=False)
            context['demands'] = items.filter(demand=True)

            tq = Q(user_from=u) | Q(user_to=u)
            tq2 = Q(status__in=['US1', 'US2'])
            context['swaps'] = Swap.objects.filter(tq).filter(tq2)

        return context

    def get(self, request):
        self.request = request
        return super(Index, self).get(request)

    def messages_for_user(self):
        u = self.request.user
        if u.is_anonymous():
            return WallMessage.objects.filter(private=False)

        groups = [i.group for i in Membership.objects.filter(user=u)]
        wall, created = Wall.objects.get_or_create(user=u, name="%s wall" % u.username)
        # user wall messages
        query = Q(wall=wall)
        # and user sended messages
        query = query | Q(user=u)
        # and user groups messages
        query = query | Q(wall__group__in=groups)
        # TODO add friends messages
        return WallMessage.objects.filter(query)


############
#          #
#  PEOPLE  #
#          #
############

class ViewProfile(TemplateView):
    template_name = 'truekko/view_profile.html'

    def get_context_data(self, **kwargs):
        context = super(ViewProfile, self).get_context_data(**kwargs)
        u = get_object_or_404(User, username=self.username)
        wall, created = Wall.objects.get_or_create(user=u, name="%s wall" % u.username)
        messages = wall.messages_for_user(self.request.user)

        context['klass'] = 'people'
        context['menu'] = generate_menu()
        context['viewing'] = u
        context['admin'] = self.request.user.get_profile().is_admin_user(u)
        context['wall'] = wall
        context['wallmessages'] = paginate(self.request, messages, 20)

        items = Item.objects.filter(user=u)
        context['offers'] = items.filter(demand=False)
        context['demands'] = items.filter(demand=True)
        return context

    def get(self, request, username):
        self.request = request
        self.username = username
        return super(ViewProfile, self).get(request)


class EditProfile(TemplateView):
    template_name = 'truekko/edit_profile.html'

    def get_context_data(self, **kwargs):
        context = super(EditProfile, self).get_context_data(**kwargs)
        context['form'] = UserProfileForm(instance=self.request.user.get_profile())
        context['klass'] = 'people'
        context['viewing'] = self.request.user
        context['menu'] = generate_menu()
        return context

    def get(self, request):
        self.request = request
        return super(EditProfile, self).get(request)

    def post(self, request):
        data = request.POST

        files_req = request.FILES
        if (files_req.get('photo', '')):
            files_req['photo'].name = request.user.username

        form = UserProfileForm(request.POST, files_req, instance=request.user.get_profile())
        if not form.is_valid():
            menu = generate_menu()
            context = RequestContext(request, {'viewing': request.user, 'form': form, 'menu': menu})
            context['klass'] = 'people'
            return render_to_response(EditProfile.template_name, context)

        form.save()

        nxt = redirect('view_profile', request.user.username)
        return nxt


class EditProfileAdmin(TemplateView):
    template_name = 'truekko/edit_profile.html'

    def get_context_data(self, **kwargs):
        context = super(EditProfileAdmin, self).get_context_data(**kwargs)
        context['form'] = UserProfileForm(instance=self.user.get_profile())
        context['klass'] = 'people'
        context['viewing'] = self.user
        context['menu'] = generate_menu()
        return context

    def get(self, request, username):
        self.request = request
        self.user = get_object_or_404(User, username=username)
        if not self.request.user.get_profile().is_admin_user(self.user):
            raise Http404
        return super(EditProfileAdmin, self).get(request)

    def post(self, request, username):
        self.user = get_object_or_404(User, username=username)
        if not self.request.user.get_profile().is_admin_user(self.user):
            raise Http404

        data = request.POST

        files_req = request.FILES
        if (files_req.get('photo', '')):
            files_req['photo'].name = self.user.username

        form = UserProfileForm(request.POST, files_req, instance=self.user.get_profile())
        if not form.is_valid():
            menu = generate_menu()
            context = RequestContext(request, {'viewing': self.user, 'form': form, 'menu': menu})
            context['klass'] = 'people'
            return render_to_response(EditProfileAdmin.template_name, context)

        form.save()

        nxt = redirect('view_profile', username)
        return nxt


class People(TemplateView):
    template_name = 'truekko/people.html'

    def get_context_data(self, **kwargs):
        context = super(People, self).get_context_data(**kwargs)
        context['klass'] = 'people'
        context['menu'] = generate_menu("people")

        q = self.request.GET.get('search', '')
        if q:
            k = Q(username__icontains=q) |\
                Q(email__icontains=q) |\
                Q(userprofile__description__icontains=q) |\
                Q(userprofile__name__icontains=q) |\
                Q(userprofile__location__icontains=q)

            query = User.objects.filter(k)
        else:
            # TODO show only latest interesting users (friends, group, others)
            query = User.objects.filter(is_active=True)
        context['users'] = paginate(self.request, query, 10)
        return context


class RateUser(View):
    def post(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        try:
            rating = int(request.POST['rating'])
        except:
            messages.info(request, _(u"Error receiving the rating"))
            return redirect('view_profile', user.username)

        if user == request.user:
            messages.info(request, _(u"You don't have permissions to rate this user"))
            return redirect('view_profile', user.username)

        if 1 > rating > 5:
            messages.info(request, _(u"Rating must be between 1 and 5"))
            return redirect('view_profile', user.username)

        user.get_profile().rating.add(score=rating,
                                      user=request.user,
                                      ip_address=request.META['REMOTE_ADDR'])
        messages.info(request, _(u"User rated successfully"))

        return redirect('view_profile', user.username)


############
#          #
#  GROUPS  #
#          #
############


class Groups(TemplateView):
    template_name = 'truekko/groups.html'

    def get_context_data(self, **kwargs):
        context = super(Groups, self).get_context_data(**kwargs)
        context['klass'] = 'group'
        context['menu'] = generate_menu("group")

        q = self.request.GET.get('search', '')
        if q:
            k = Q(email__icontains=q) |\
                Q(description__icontains=q) |\
                Q(name__icontains=q) |\
                Q(location__icontains=q)

            query = Group.objects.filter(k)
        else:
            # TODO show only latest interesting groups (membership, friends, others)
            query = Group.objects.all()
        context['groups'] = paginate(self.request, query, 10)
        return context


class ViewGroup(TemplateView):
    template_name = 'truekko/view_group.html'

    def get_context_data(self, **kwargs):
        context = super(ViewGroup, self).get_context_data(**kwargs)
        context['klass'] = 'group'
        context['menu'] = generate_menu('group')
        context['viewing'] = get_object_or_404(Group, pk=self.groupid)

        context['editable'] = is_group_editable(self.request.user.username, self.groupid)
        context['member'] = is_member(self.request.user, context['viewing'])

        g = get_object_or_404(Group, pk=self.groupid)
        context['requests'] = g.membership_set.filter(role="REQ").count()
        context['memberships'] = g.membership_set.exclude(role__in=["REQ", "BAN"]).order_by("-id")

        wall, created = Wall.objects.get_or_create(group=g, name="%s wall" % g.name)
        messages = wall.messages_for_user(self.request.user)

        context['wall'] = wall
        context['wallmessages'] = paginate(self.request, messages, 20)
        return context

    def get(self, request, groupid):
        self.request = request
        self.groupid = groupid
        return super(ViewGroup, self).get(request)


class EditGroup(TemplateView):
    template_name = 'truekko/edit_group.html'

    def get_context_data(self, **kwargs):
        context = super(EditGroup, self).get_context_data(**kwargs)
        g = get_object_or_404(Group, pk=self.groupid)
        context['form'] = GroupForm(instance=g)
        context['klass'] = 'group'
        context['group'] = g
        context['menu'] = generate_menu("group")
        return context

    def get(self, request, groupid):
        self.request = request
        self.groupid = groupid
        return super(EditGroup, self).get(request)

    def post(self, request, groupid):
        self.groupid = groupid
        g = get_object_or_404(Group, pk=self.groupid)
        data = request.POST

        files_req = request.FILES
        if (files_req.get('photo', '')):
            files_req['photo'].name = "group_%s" % g.id

        form = GroupForm(request.POST, files_req, instance=g)
        if not form.is_valid():
            menu = generate_menu("group")
            context = RequestContext(request, {'group': g, 'form': form, 'menu': menu})
            context['klass'] = 'group'
            return render_to_response(EditGroup.template_name, context)

        form.save()

        nxt = redirect('view_group', groupid)
        return nxt


class EditGroupMembers(TemplateView):
    template_name = 'truekko/edit_group_members.html'

    def get_context_data(self, **kwargs):
        context = super(EditGroupMembers, self).get_context_data(**kwargs)
        g = get_object_or_404(Group, pk=self.groupid)
        context['form'] = GroupForm(instance=g)
        context['klass'] = 'group'
        context['group'] = g
        context['requests'] = g.membership_set.filter(role="REQ").order_by("-id")
        context['memberships'] = g.membership_set.exclude(role__in=["REQ", "BAN"]).order_by("-id")
        context['banned'] = g.membership_set.filter(role="BAN").order_by("-id")
        context['menu'] = generate_menu("group")
        return context

    def get(self, request, groupid):
        self.request = request
        self.groupid = groupid
        return super(EditGroupMembers, self).get(request)

    def post(self, request, groupid):
        self.groupid = groupid
        g = get_object_or_404(Group, pk=self.groupid)
        data = request.POST

        def notify_user(user):
            context = {'group': g, 'user': user, 'url': reverse('view_group', args=[groupid])}
            template_email('truekko/user_member_mail.txt',
                           _("Membership request confirmed %s") % g.name,
                           [user.email], context)

        for k, v in data.items():
            if k.startswith("role_"):
                role, uid = k.split("_")
                m = Membership.objects.get(user__id=uid, group=g)
                if data[k] == "admin":
                    if m.role == "REQ":
                        notify_user(m.user)
                    m.role = "ADM"
                    m.save()
                elif data[k] == "req":
                    m.role = "REQ"
                    m.save()
                elif data[k] == "member":
                    if m.role == "REQ":
                        notify_user(m.user)
                    m.role = "MEM"
                    m.save()
                elif data[k] == "ban":
                    m.role = "BAN"
                    m.save()
                elif data[k] == "remove":
                    m.delete()

                if not m.user.is_active and data[k] in ["admin", "member"]:
                    m.user.is_active = True
                    m.user.save()

        messages.info(request, _("Group memebership modified correctly"))

        nxt = redirect('view_group', groupid)
        return nxt


class Register(TemplateView):

    template_name = 'truekko/register.html'

    def get_context_data(self, **kwargs):
        context = super(Register, self).get_context_data(**kwargs)
        g = get_object_or_404(Group, pk=self.groupid)
        context['form'] = RegisterForm()
        context['klass'] = 'group'
        context['group'] = g
        context['menu'] = generate_menu("group")
        return context

    def get(self, request, groupid):
        self.request = request
        self.groupid = groupid
        return super(Register, self).get(request)

    def post(self, request, groupid):
        self.groupid = groupid
        g = get_object_or_404(Group, pk=self.groupid)
        data = request.POST

        f = RegisterForm(data)
        if not f.is_valid():
            context = RequestContext(request, {})
            context['klass'] = 'group'
            context['group'] = g
            context['menu'] = generate_menu("group")
            context['form'] = f
            return render_to_response(Register.template_name, context)

        f.save(g)

        # sending mail to user and admins
        context = dict(f.data.items())
        context['group'] = g
        template_email('truekko/user_registered_mail.txt', _("Welcome to etruekko"), [f.data['email']], context)
        context['url'] = reverse('edit_group_members', args=(groupid,))
        template_email('truekko/user_registered_admin_mail.txt',
                       _("New user '%s' in group '%s'") % (f.data['username'], g.name),
                       g.admins_emails(), context)

        nxt = redirect('register_confirm', groupid)
        return nxt


class RegisterAdmin(TemplateView):

    template_name = 'truekko/register_admin.html'

    def get_context_data(self, **kwargs):
        context = super(RegisterAdmin, self).get_context_data(**kwargs)
        g = get_object_or_404(Group, pk=self.groupid)
        context['form'] = RegisterForm()
        context['klass'] = 'group'
        context['group'] = g
        context['menu'] = generate_menu("group")
        return context

    def get_context(self, data):
        context = RequestContext(self.request, data)
        context['klass'] = 'group'
        context['menu'] = generate_menu("group")
        return context

    def get(self, request, groupid):
        self.request = request
        self.groupid = groupid
        return super(RegisterAdmin, self).get(request)

    def post(self, request, groupid):
        self.groupid = groupid
        g = get_object_or_404(Group, pk=self.groupid)
        data = request.POST

        if 'existing' in data:
            username = data.get('existinguser', '')
            try:
                u = User.objects.get(username=username)
            except:
                msg = _("The user '%s' doesn't exist") % username
                messages.info(request, msg)
                return render_to_response(RegisterAdmin.template_name,
                                          self.get_context({'group': g, 'form': RegisterForm()}))
                return redirect('edit_group_members', groupid)

            if (Membership.objects.filter(user=u, group=g).count()):
                msg = _("The user '%s' is already member of the group") % username
                messages.info(request, msg)
                return render_to_response(RegisterAdmin.template_name,
                                          self.get_context({'group': g, 'form': RegisterForm()}))
                return redirect('edit_group_members', groupid)

            m = Membership(user=u, group=g, role='REQ')
            m.save()

            msg = _("A new membership request has been created, you need to confirm")
            messages.info(request, msg)
            return redirect('edit_group_members', groupid)

        f = RegisterForm(data)
        if not f.is_valid():
            return render_to_response(RegisterAdmin.template_name,
                                      self.get_context({'group': g, 'form': f}))

        f.save(g)

        # sending mail to user
        context = dict(f.data.items())
        context['group'] = g
        template_email('truekko/user_registered_mail.txt', _("Welcome to etruekko"), [context['email']], context)

        nxt = redirect('edit_group_members', groupid)
        return nxt


class RegisterConfirm(TemplateView):
    template_name = 'truekko/register_confirm.html'

    def get_context_data(self, **kwargs):
        context = super(RegisterConfirm, self).get_context_data(**kwargs)
        g = get_object_or_404(Group, pk=self.groupid)
        context['klass'] = 'group'
        context['group'] = g
        context['menu'] = generate_menu("group")
        return context

    def get(self, request, groupid):
        self.request = request
        self.groupid = groupid
        return super(RegisterConfirm, self).get(request)


class JoinGroup(View):

    def post(self, request, groupid):
        g = get_object_or_404(Group, pk=groupid)
        data = request.POST

        if request.user.is_anonymous():
            return redirect('register_group', groupid)

        if is_member(request.user, g):
            msg = _("You already are member of this group")
        else:
            m = Membership(user=request.user, group=g, role='REQ')
            m.save()
            # sending email to group admin
            context = {'group': g, 'username': request.user.username, 'user': request.user,
                       'url': reverse('edit_group_members', args=(groupid,))}
            template_email('truekko/user_registered_admin_mail.txt',
                           _("New user '%s' in group '%s'") % (request.user.username, g.name),
                           g.admins_emails(), context)

            msg = _("Your membership request has been sent to group administrator")

        messages.info(request, msg)
        nxt = redirect('view_group', groupid)
        return nxt


class LeaveGroup(View):

    def post(self, request, groupid):
        g = get_object_or_404(Group, name=groupid)
        data = request.POST

        if is_member(request.user, g):
            m = Membership.objects.get(user=request.user, group=g)
            m.delete()
            # TODO send email to group admin

        msg = _("You are not member of this group")

        messages.info(request, msg)
        nxt = redirect('view_group', groupid)
        return nxt


#############
#           #
# TRANSFER  #
#           #
#############


class TransferDirect(TemplateView):
    template_name = 'truekko/transfer_direct.html'

    def get_context(self, data):
        context = RequestContext(self.request, data)
        context['klass'] = 'transf'
        context['menu'] = generate_menu("transf")
        return context

    def get_context_data(self, **kwargs):
        context = super(TransferDirect, self).get_context_data(**kwargs)
        u = get_object_or_404(User, username=self.username)
        context['user_to'] = u
        context['form'] = TransferDirectForm(self.request.user, u)
        context['klass'] = 'transf'
        context['menu'] = generate_menu("transf")
        return context

    def get(self, request, username):
        self.request = request
        self.username = username
        return super(TransferDirect, self).get(request)

    def post(self, request, username):
        self.request = request
        self.username = username
        u = get_object_or_404(User, username=self.username)
        data = request.POST

        f = TransferDirectForm(self.request.user, u, data)
        if not f.is_valid():
            return render_to_response(TransferDirect.template_name,
                                      self.get_context({'user_to': u, 'form': f}))

        f.save()

        # sending mail to both users
        context = dict(f.data.items())
        context['user_from'] = request.user
        context['user_to'] = u
        #template_email('truekko/transfer_direct_mail.txt', _("Direct transfer"), [u.email, request.user.email], context)
        messages.info(request, _("Transfer has been made correctly"))

        nxt = redirect('view_profile', u.username)
        return nxt


class TransferList(TemplateView):
    template_name = 'truekko/transfer_list.html'

    def get_context_data(self, **kwargs):
        context = super(TransferList, self).get_context_data(**kwargs)
        context['klass'] = 'transf'
        context['menu'] = generate_menu("transf")

        tq = Q(user_from=self.request.user) | Q(user_to=self.request.user)
        query = Transfer.objects.filter(tq)

        q = self.request.GET.get('search', '')
        if q:
            k = Q(user_from__username__icontains=q) |\
                Q(user_from__email__icontains=q) |\
                Q(user_from__userprofile__name__icontains=q) |\
                Q(user_from__userprofile__location__icontains=q) |\
                Q(user_to__username__icontains=q) |\
                Q(user_to__email__icontains=q) |\
                Q(user_to__userprofile__name__icontains=q) |\
                Q(user_to__userprofile__location__icontains=q)

            query = query.filter(k)

        query = query.order_by('-date')[:20]

        query2 = Swap.objects.filter(tq)
        if q:
            k = Q(user_from__username__icontains=q) |\
                Q(user_from__email__icontains=q) |\
                Q(user_from__userprofile__name__icontains=q) |\
                Q(user_from__userprofile__location__icontains=q) |\
                Q(user_to__username__icontains=q) |\
                Q(user_to__email__icontains=q) |\
                Q(user_to__userprofile__name__icontains=q) |\
                Q(user_to__userprofile__location__icontains=q)

            query2 = query2.filter(k).order_by('-date')[:20]

        queries = [i for i in query] + [i for i in query2]
        queries = sorted(queries, key=lambda x: x.date, reverse=True)

        context['transfs'] = paginate(self.request, queries, 20)
        return context

    def get(self, request):
        self.request = request
        return super(TransferList, self).get(request)


########
#      #
# SWAP #
#      #
########


class SwapCreation(TemplateView):
    template_name = 'truekko/swap_creation.html'

    def get_context(self, data):
        context = RequestContext(self.request, data)
        context['klass'] = 'transf'
        context['menu'] = generate_menu("transf")
        return context

    def get_context_data(self, **kwargs):
        context = super(SwapCreation, self).get_context_data(**kwargs)
        u = get_object_or_404(User, username=self.username)
        context = self.get_context({'user_to': u, 'user_from': self.request.user})
        context['items'] = [int(i) for i in self.request.GET.getlist('item')]
        return context

    def get(self, request, username):
        self.request = request
        self.username = username
        return super(SwapCreation, self).get(request)

    def post(self, request, username):
        self.request = request
        self.username = username
        u = get_object_or_404(User, username=self.username)
        data = request.POST

        items = []
        for k in data.keys():
            if k.startswith('item_'):
                items.append(int(k.split('_')[1]))

        try:
            credits = data.get('credits', 0)
            credits = int(credits if credits else 0)
        except:
            context = self.get_context({'user_to': u, 'user_from': self.request.user})
            context['items'] = items
            context['errors'] = [_('Invalid credits')]
            return render_to_response(SwapCreation.template_name, context)

        swap = Swap(status="US1",
                    credits=credits,
                    user_from=self.request.user,
                    user_to=u)
        swap.save()

        for item in items:
            i = Item.objects.get(id=item)
            si = SwapItems(swap=swap, item=i)
            si.save()

        comment = data.get('comment', '')
        if comment:
            swap_comment = SwapComment(swap=swap,
                                       user=self.request.user,
                                       comment=comment)
            swap_comment.save()

        nxt = redirect('swap_view', swap.id)
        return nxt


class SwapView(TemplateView):
    template_name = 'truekko/swap_creation.html'

    def get_context(self, data):
        context = RequestContext(self.request, data)
        context['klass'] = 'transf'
        context['menu'] = generate_menu("transf")
        return context

    def get_context_data(self, **kwargs):
        context = super(SwapView, self).get_context_data(**kwargs)
        context = self.get_context({'user_to': self.swap.user_to,
                                    'user_from': self.swap.user_from})
        context['items'] = [item.item.id for item in self.swap.items.all()]
        context['credits'] = self.swap.credits
        context['comments'] = self.swap.comments.all()
        context['swap'] = self.swap
        if self.request.user == self.swap.user_from and self.swap.status == 'US2':
            context['accept'] = True
        if self.request.user == self.swap.user_to and self.swap.status == 'US1':
            context['accept'] = True

        context['swapstatus'] = self.swap.get_status_msg()

        return context

    def get(self, request, swapid):
        self.request = request
        self.swap = get_object_or_404(Swap, id=swapid)
        if request.user != self.swap.user_to and\
           request.user != self.swap.user_from:
            messages.info(request, _("You can't view this swap"))
            return redirect('/')

        return super(SwapView, self).get(request)

    def post(self, request, swapid):
        self.request = request
        self.swap = get_object_or_404(Swap, id=swapid)
        data = request.POST

        # comment
        comment = data.get('comment', '')
        if comment:
            swap_comment = SwapComment(swap=self.swap,
                                       user=self.request.user,
                                       comment=comment)
            swap_comment.save()

        if 'cancel' in data.keys():
            self.swap.delete()
            messages.info(request, _("Swap canceled"))
            return redirect('/')

        if 'accept' in data.keys():
            nxt = redirect('swap_view', self.swap.id)
            if self.request.user == self.swap.user_to and self.swap.status != 'US1':
                return nxt
            if self.request.user == self.swap.user_from and self.swap.status != 'US2':
                return nxt

            self.swap.status = 'CON'
            self.swap.save()
            messages.info(request, _("Conglatulations, swap has been accepted"))
            # TODO notify users by mail
            return nxt

        items = []
        for k in data.keys():
            if k.startswith('item_'):
                items.append(int(k.split('_')[1]))

        try:
            credits = data.get('credits', 0)
            credits = int(credits if credits else 0)
        except:
            context = self.get_context({'user_to': self.swap.user_to,
                                        'user_from': self.swap.user_from})
            context['items'] = items
            context['errors'] = [_('Invalid credits')]
            return render_to_response(SwapView.template_name, context)

        self.swap.credits = credits
        self.swap.save()

        for swap_item in self.swap.items.all():
            if swap_item.item.id not in items:
                swap_item.delete()

        for item in items:
            i = Item.objects.get(id=item)
            si, created = SwapItems.objects.get_or_create(swap=self.swap, item=i)
            if created:
                si.save()

        if 'offer' in data.keys():
            if self.request.user == self.swap.user_to:
                self.swap.status = 'US2'
            if self.request.user == self.swap.user_from:
                self.swap.status = 'US1'
            # TODO notify users by mail

            self.swap.save()

        nxt = redirect('swap_view', self.swap.id)
        return nxt


class SwapList(TemplateView):
    template_name = 'truekko/swap_list.html'

    def get_context_data(self, **kwargs):
        context = super(SwapList, self).get_context_data(**kwargs)
        context['klass'] = 'transf'
        context['menu'] = generate_menu("transf")

        tq = Q(user_from=self.request.user) | Q(user_to=self.request.user)
        query = Swap.objects.filter(tq)

        q = self.request.GET.get('search', '')
        if q:
            k = Q(user_from__username__icontains=q) |\
                Q(user_from__email__icontains=q) |\
                Q(user_from__userprofile__name__icontains=q) |\
                Q(user_from__userprofile__location__icontains=q) |\
                Q(user_to__username__icontains=q) |\
                Q(user_to__email__icontains=q) |\
                Q(user_to__userprofile__name__icontains=q) |\
                Q(user_to__userprofile__location__icontains=q)

            query = query.filter(k)

        context['swaps'] = paginate(self.request, query.order_by('status'), 10)
        return context

    def get(self, request):
        self.request = request
        return super(SwapList, self).get(request)



###########
#         #
#  ITEMS  #
#         #
###########


class ItemAdd(TemplateView):
    template_name = 'truekko/item_add.html'

    def get_context(self, data):
        context = RequestContext(self.request, data)
        context['klass'] = 'add'
        context['menu'] = generate_menu("add")
        if self.item:
            context['form'] = ItemAddForm(instance=self.item)
            context['editing'] = True
        else:
            context['form'] = ItemAddForm()
        return context

    def get_context_data(self, **kwargs):
        context = super(ItemAdd, self).get_context_data(**kwargs)
        context = self.get_context(context)
        return context

    def get(self, request, object_id=None):
        self.request = request
        self.item = None
        if object_id:
            self.item = get_object_or_404(Item, id=object_id, user=self.request.user)
        return super(ItemAdd, self).get(request)

    def post(self, request, object_id=None):
        self.item = None
        if object_id:
            self.item = get_object_or_404(Item, id=object_id, user=self.request.user)

        files_req = request.FILES
        if (files_req.get('photo', '')):
            files_req['photo'].name = "item_%s" % uuid.uuid4().hex

        if self.item:
            form = ItemAddForm(request.POST, files_req, instance=self.item)
        else:
            form = ItemAddForm(request.POST, files_req)

        if not form.is_valid():
            context = self.get_context({})
            context['form'] = form
            return render_to_response(ItemAdd.template_name, context)

        item = form.save(commit=False)
        item.user = self.request.user
        item.save()

        # parsing tags
        tags = request.POST.get('tags')
        if tags:
            tagnames = (i.strip() for i in request.POST.get('tags').split(','))
            for tag in tagnames:
                dbtag, created = Tag.objects.get_or_create(name=tag)
                it, created = ItemTagged.objects.get_or_create(item=item, tag=dbtag)

        nxtsrv = 'item'
        if item.type == "IT":
            messages.info(request, _("Item added correctly"))
        else:
            messages.info(request, _("Service added correctly"))
            nxtsrv = 'serv'

        nxt = redirect('item_list', nxtsrv, request.user.username)
        return nxt


class ItemView(TemplateView):
    template_name = 'truekko/item_view.html'

    def get_context_data(self, **kwargs):
        context = super(ItemView, self).get_context_data(**kwargs)

        item = get_object_or_404(Item, pk=self.itemid)
        if item.type == "IT":
            klass = 'item'
        else:
            klass = 'serv'

        context['klass'] = klass
        context['menu'] = generate_menu(klass)
        context['item'] = item
        return context

    def get(self, request, itemid):
        self.request = request
        self.itemid = itemid

        return super(ItemView, self).get(request)


class ItemList(TemplateView):
    template_name = 'truekko/item_list.html'

    def get_context_data(self, **kwargs):
        context = super(ItemList, self).get_context_data(**kwargs)
        context['klass'] = self.klass
        context['menu'] = generate_menu(self.klass)

        if self.username:
            iq = Q(user__username=self.username) & Q(type=self.itemtype)
        else:
            iq = Q(type=self.itemtype)

        query = Item.objects.filter(iq)

        q = self.request.GET.get('search', '')
        if q:
            k = Q(name__icontains=q) |\
                Q(description__icontains=q) |\
                Q(user__username__icontains=q) |\
                Q(user__userprofile__location__icontains=q) |\
                Q(user__userprofile__name__icontains=q)

            itemtagged = ItemTagged.objects.filter(tag__name__icontains=q)
            for it in itemtagged:
                k = k | Q(itemtagged=it)

            query = query.filter(k).distinct()

        context['items'] = paginate(self.request, query.order_by('-pub_date'), 10)
        return context

    def get(self, request, itemtype, username=None):
        self.request = request

        if itemtype == "item":
            self.itemtype = "IT"
            self.klass = 'item'
        else:
            self.itemtype = "SR"
            self.klass = 'serv'
        self.username = username

        return super(ItemList, self).get(request)


class ItemRemove(TemplateView):
    template_name = 'truekko/item_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super(ItemRemove, self).get_context_data(**kwargs)
        context['klass'] = self.klass
        context['menu'] = generate_menu(self.klass)
        context['item'] = self.item
        return context

    def get(self, request, itemid):
        self.request = request
        self.item = get_object_or_404(Item, pk=itemid, user=request.user)

        if self.item.type == "IT":
            self.klass = 'item'
        else:
            self.klass = 'serv'
        return super(ItemRemove, self).get(request)

    def post(self, request, itemid):
        self.request = request
        self.item = get_object_or_404(Item, pk=itemid, user=request.user)
        self.item.delete()

        messages.info(request, _(u"Item removed correctly"))

        return redirect(index)


##############
#            #
#  MESSAGES  #
#            #
##############


class MessagePost(View):

    def post(self, request, wallid):
        wall = get_object_or_404(Wall, pk=wallid)
        msg = request.POST.get('comment', '')
        priv = bool(request.POST.get('priv', False))

        # TODO check post permissions
        if not self.can_post(request.user, wall):
            messages.info(request, _(u"You can't post here"))
        else:
            wmsg = WallMessage(user=request.user,
                               wall=wall,
                               msg=msg,
                               private=priv)
            wmsg.save()
            messages.info(request, _(u"Message posted correctly"))

        # redirecting to prev page
        referer = request.META['HTTP_REFERER']
        if not referer:
            return redirect("/")

        return redirect(referer)

    def can_post(self, user, wall):
        if wall.user == user:
            return True
        if wall.group:
            return is_member(user, wall.group)

        # TODO only can post in friend walls

        return True


class MessageRemove(TemplateView):
    template_name = 'truekko/message_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super(MessageRemove, self).get_context_data(**kwargs)
        context['menu'] = generate_menu()
        context['msg'] = self.msg
        return context

    def get(self, request, msgid):
        self.request = request
        self.msg = get_object_or_404(WallMessage, pk=msgid, user=request.user)

        return super(MessageRemove, self).get(request)

    def post(self, request, msgid):
        self.request = request
        self.msg = get_object_or_404(WallMessage, pk=msgid, user=request.user)
        self.msg.delete()

        messages.info(request, _(u"Message removed correctly"))

        return redirect(index)


# profile
edit_profile = login_required(EditProfile.as_view())
edit_profile_admin = login_required(EditProfileAdmin.as_view())
view_profile = login_required(ViewProfile.as_view())
rate_user = login_required(RateUser.as_view())
people = People.as_view()

# group
groups = Groups.as_view()
view_group = ViewGroup.as_view()
edit_group = login_required(is_group_admin(EditGroup.as_view()))
edit_group_members = login_required(is_group_admin(EditGroupMembers.as_view()))
leave_group = login_required(LeaveGroup.as_view())
join_group = JoinGroup.as_view()
register_group_admin = login_required(is_group_admin(RegisterAdmin.as_view()))
register_group = Register.as_view()
register_confirm = RegisterConfirm.as_view()

# transfer
transfer_direct = login_required(TransferDirect.as_view())
transfer_list = login_required(TransferList.as_view())

# swap
swap_creation = login_required(SwapCreation.as_view())
swap_view = login_required(SwapView.as_view())
swap_list = login_required(SwapList.as_view())

#item
item_add = login_required(ItemAdd.as_view())
item_view = login_required(ItemView.as_view())
item_list = login_required(ItemList.as_view())
item_remove = login_required(ItemRemove.as_view())

# messages
message_post = login_required(MessagePost.as_view())
message_remove = login_required(MessageRemove.as_view())

index = Index.as_view()
