from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from django import forms
from django.forms.widgets import ClearableFileInput

from truekko.models import UserProfile
from truekko.models import Group
from truekko.models import User
from truekko.models import Membership


class CustomImageWidget(ClearableFileInput):

    template_with_initial = u'%(clear_template)s<br />%(input_text)s: %(input)s'


class UserProfileForm(ModelForm):

    class Meta:
        model = UserProfile
        fields = ('photo', 'name', 'location', 'web', 'description')
        widgets = {'photo': CustomImageWidget()}


class GroupForm(ModelForm):

    class Meta:
        model = Group
        fields = ('photo', 'name', 'location', 'web', 'description')
        widgets = {'photo': CustomImageWidget()}


class RegisterForm(forms.Form):

    username = forms.CharField(label=_("Username"))
    name = forms.CharField(label=_("Name"))
    email = forms.EmailField(label=_("Email"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirm"), widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).count():
            raise forms.ValidationError(_("Username exists"))

        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).count():
            raise forms.ValidationError(_("User exists with the same email"))

        return email

    def clean(self):
        cleaned_data = self.cleaned_data
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("password2")

        if p1 != p2:
            raise forms.ValidationError(_("Password and password confirm didn't match"))

        return cleaned_data

    def save(self, group):
        data = self.cleaned_data
        u = User(username=data["username"], email=data["email"], is_active=False)
        u.set_password(data["password"])
        u.save()
        p = u.get_profile()
        p.name = data["name"]
        p.save()

        m = Membership(user=u, group=group, role="REQ")
        m.save()
