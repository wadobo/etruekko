from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import View, TemplateView
from django.contrib.auth.decorators import login_required
from decorators import is_group_admin, is_group_editable, is_member
from django.shortcuts import render_to_response
from django.db.models import Q

from truekko.forms import UserProfileForm
from truekko.forms import GroupForm
from truekko.forms import RegisterForm
from truekko.forms import TransferDirectForm
from truekko.models import UserProfile
from truekko.models import User
from truekko.models import Group
from truekko.models import Membership
from truekko.models import Transfer
from truekko.utils import generate_menu
from etruekko.utils import paginate, template_email


class Index(TemplateView):
    template_name = 'truekko/index.html'

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['klass'] = 'home'
        context['menu'] = generate_menu("home")
        return context


############
#          #
#  PEOPLE  #
#          #
############

class ViewProfile(TemplateView):
    template_name = 'truekko/view_profile.html'

    def get_context_data(self, **kwargs):
        context = super(ViewProfile, self).get_context_data(**kwargs)
        context['klass'] = 'people'
        context['menu'] = generate_menu()
        context['viewing'] = get_object_or_404(User, username=self.username)
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
            context = RequestContext(request, {'user': request.user, 'form': form, 'menu': menu})
            context['klass'] = 'people'
            return render_to_response(EditProfile.template_name, context)

        form.save()

        nxt = redirect('view_profile', request.user.username)
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
        context['viewing'] = get_object_or_404(Group, name=self.groupname)

        context['editable'] = is_group_editable(self.request.user.username, self.groupname)
        context['member'] = is_member(self.request.user, context['viewing'])

        g = get_object_or_404(Group, name=self.groupname)
        context['requests'] = g.membership_set.filter(role="REQ").count()
        context['memberships'] = g.membership_set.exclude(role__in=["REQ", "BAN"]).order_by("-id")
        return context

    def get(self, request, groupname):
        self.request = request
        self.groupname = groupname
        return super(ViewGroup, self).get(request)


class EditGroup(TemplateView):
    template_name = 'truekko/edit_group.html'

    def get_context_data(self, **kwargs):
        context = super(EditGroup, self).get_context_data(**kwargs)
        g = get_object_or_404(Group, name=self.groupname)
        context['form'] = GroupForm(instance=g)
        context['klass'] = 'group'
        context['group'] = g
        context['menu'] = generate_menu("group")
        return context

    def get(self, request, groupname):
        self.request = request
        self.groupname = groupname
        return super(EditGroup, self).get(request)

    def post(self, request, groupname):
        self.groupname = groupname
        g = get_object_or_404(Group, name=self.groupname)
        data = request.POST

        files_req = request.FILES
        if (files_req.get('photo', '')):
            files_req['photo'].name = groupname

        form = GroupForm(request.POST, files_req, instance=g)
        if not form.is_valid():
            menu = generate_menu("group")
            context = RequestContext(request, {'group': g, 'form': form, 'menu': menu})
            context['klass'] = 'group'
            return render_to_response(EditGroup.template_name, context)

        form.save()

        nxt = redirect('view_group', groupname)
        return nxt


class EditGroupMembers(TemplateView):
    template_name = 'truekko/edit_group_members.html'

    def get_context_data(self, **kwargs):
        context = super(EditGroupMembers, self).get_context_data(**kwargs)
        g = get_object_or_404(Group, name=self.groupname)
        context['form'] = GroupForm(instance=g)
        context['klass'] = 'group'
        context['group'] = g
        context['requests'] = g.membership_set.filter(role="REQ").order_by("-id")
        context['memberships'] = g.membership_set.exclude(role__in=["REQ", "BAN"]).order_by("-id")
        context['banned'] = g.membership_set.filter(role="BAN").order_by("-id")
        context['menu'] = generate_menu("group")
        return context

    def get(self, request, groupname):
        self.request = request
        self.groupname = groupname
        return super(EditGroupMembers, self).get(request)

    def post(self, request, groupname):
        self.groupname = groupname
        g = get_object_or_404(Group, name=self.groupname)
        data = request.POST

        def notify_user(user):
            context = {'group': g, 'user': user, 'url': reverse('view_group', args=[groupname])}
            template_email('truekko/user_member_mail.txt',
                           _("Membership request confirmed %s") % groupname,
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

        request.user.message_set.create(message=_("Group memebership modified correctly"))

        nxt = redirect('view_group', groupname)
        return nxt


class Register(TemplateView):

    template_name = 'truekko/register.html'

    def get_context_data(self, **kwargs):
        context = super(Register, self).get_context_data(**kwargs)
        g = get_object_or_404(Group, name=self.groupname)
        context['form'] = RegisterForm()
        context['klass'] = 'group'
        context['group'] = g
        context['menu'] = generate_menu("group")
        return context

    def get(self, request, groupname):
        self.request = request
        self.groupname = groupname
        return super(Register, self).get(request)

    def post(self, request, groupname):
        self.groupname = groupname
        g = get_object_or_404(Group, name=self.groupname)
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
        context['url'] = reverse('edit_group_members', args=(groupname,))
        template_email('truekko/user_registered_admin_mail.txt',
                       _("New user '%s' in group '%s'") % (f.data['username'], groupname),
                       g.admins_emails(), context)

        nxt = redirect('register_confirm', groupname)
        return nxt


class RegisterAdmin(TemplateView):

    template_name = 'truekko/register_admin.html'

    def get_context_data(self, **kwargs):
        context = super(RegisterAdmin, self).get_context_data(**kwargs)
        g = get_object_or_404(Group, name=self.groupname)
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

    def get(self, request, groupname):
        self.request = request
        self.groupname = groupname
        return super(RegisterAdmin, self).get(request)

    def post(self, request, groupname):
        self.groupname = groupname
        g = get_object_or_404(Group, name=self.groupname)
        data = request.POST

        if 'existing' in data:
            username = data.get('existinguser', '')
            try:
                u = User.objects.get(username=username)
            except:
                msg = _("The user '%s' doesn't exist") % username
                request.user.message_set.create(message=msg)
                return render_to_response(RegisterAdmin.template_name,
                                          self.get_context({'group': g, 'form': RegisterForm()}))
                return redirect('edit_group_members', groupname)

            if (Membership.objects.filter(user=u, group=g).count()):
                msg = _("The user '%s' is already member of the group") % username
                request.user.message_set.create(message=msg)
                return render_to_response(RegisterAdmin.template_name,
                                          self.get_context({'group': g, 'form': RegisterForm()}))
                return redirect('edit_group_members', groupname)

            m = Membership(user=u, group=g, role='REQ')
            m.save()

            msg = _("A new membership request has been created, you need to confirm")
            request.user.message_set.create(message=msg)
            return redirect('edit_group_members', groupname)

        f = RegisterForm(data)
        if not f.is_valid():
            return render_to_response(RegisterAdmin.template_name,
                                      self.get_context({'group': g, 'form': f}))

        f.save(g)

        # sending mail to user
        context = dict(f.data.items())
        context['group'] = g
        template_email('truekko/user_registered_mail.txt', _("Welcome to etruekko"), [context['email']], context)

        nxt = redirect('edit_group_members', groupname)
        return nxt


class RegisterConfirm(TemplateView):
    template_name = 'truekko/register_confirm.html'

    def get_context_data(self, **kwargs):
        context = super(RegisterConfirm, self).get_context_data(**kwargs)
        g = get_object_or_404(Group, name=self.groupname)
        context['klass'] = 'group'
        context['group'] = g
        context['menu'] = generate_menu("group")
        return context

    def get(self, request, groupname):
        self.request = request
        self.groupname = groupname
        return super(RegisterConfirm, self).get(request)


class JoinGroup(View):

    def post(self, request, groupname):
        g = get_object_or_404(Group, name=groupname)
        data = request.POST

        if request.user.is_anonymous():
            return redirect('register_group', groupname)

        if is_member(request.user, g):
            msg = _("You already are member of this group")
        else:
            m = Membership(user=request.user, group=g, role='REQ')
            m.save()
            # sending email to group admin
            context = {'group': g, 'username': request.user.username, 'user': request.user,
                       'url': reverse('edit_group_members', args=(groupname,))}
            template_email('truekko/user_registered_admin_mail.txt',
                           _("New user '%s' in group '%s'") % (request.user.username, groupname),
                           g.admins_emails(), context)

            msg = _("Your membership request has been sent to group administrator")

        request.user.message_set.create(message=msg)
        nxt = redirect('view_group', groupname)
        return nxt


class LeaveGroup(View):

    def post(self, request, groupname):
        g = get_object_or_404(Group, name=groupname)
        data = request.POST

        if is_member(request.user, g):
            m = Membership.objects.get(user=request.user, group=g)
            m.delete()
            # TODO send email to group admin

        msg = _("You are not member of this group")

        request.user.message_set.create(message=msg)
        nxt = redirect('view_group', groupname)
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
        request.user.message_set.create(message=_("Transfer has been made correctly"))

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

        context['transfs'] = paginate(self.request, query.order_by('-date'), 10)
        return context

    def get(self, request):
        self.request = request
        return super(TransferList, self).get(request)


edit_profile = login_required(EditProfile.as_view())
view_profile = login_required(ViewProfile.as_view())
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

index = Index.as_view()
