from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import View, TemplateView
from django.contrib.auth.decorators import login_required
from decorators import is_group_admin, is_group_editable
from django.shortcuts import render_to_response
from django.db.models import Q

from truekko.forms import UserProfileForm
from truekko.forms import GroupForm
from truekko.models import UserProfile
from truekko.models import User
from truekko.models import Group
from truekko.utils import generate_menu
from etruekko.utils import paginate


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
            context = {'user': request.user, 'form': form, 'menu': menu}
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
            query = User.objects.all()
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
        # TODO check user group relation
        context['editable'] = is_group_editable(self.request.user.username, self.groupname)
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
            context = {'group': g, 'form': form, 'menu': menu}
            context['klass'] = 'group'
            return render_to_response(EditGroup.template_name, context)

        form.save()

        nxt = redirect('view_group', groupname)
        return nxt


edit_profile = login_required(EditProfile.as_view())
view_profile = login_required(ViewProfile.as_view())
people = People.as_view()

groups = Groups.as_view()
view_group = ViewGroup.as_view()
# TODO check group role

edit_group = login_required(is_group_admin(EditGroup.as_view()))

index = Index.as_view()
