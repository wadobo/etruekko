from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import View, TemplateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

from truekko.forms import UserProfileForm
from truekko.models import UserProfile


class EditProfile(TemplateView):
    template_name = 'truekko/edit_profile.html'

    def get_context_data(self, **kwargs):
        context = super(EditProfile, self).get_context_data(**kwargs)
        context['form'] = UserProfileForm(instance=self.request.user.get_profile())
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
            return render_to_response(EditProfile.template_name,
                                      {'user': request.user, 'form': form})

        form.save()

        nxt = redirect('/')
        return nxt


edit_profile = login_required(EditProfile.as_view())
