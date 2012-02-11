from truekko.models import UserProfile
from truekko.models import Group
from django.forms import ModelForm
from django.forms.widgets import ClearableFileInput


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
