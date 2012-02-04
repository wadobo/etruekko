from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import View, TemplateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.db.models import Q

from truekko.forms import UserProfileForm
from truekko.models import UserProfile
from truekko.models import User
from truekko.utils import generate_menu
from etruekko.utils import paginate


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

        nxt = redirect('/')
        return nxt


class Index(TemplateView):
    template_name = 'truekko/index.html'

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['klass'] = 'home'
        context['menu'] = generate_menu("home")
        return context


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


edit_profile = login_required(EditProfile.as_view())
index = Index.as_view()
people = People.as_view()
