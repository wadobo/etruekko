import re

from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from django import forms
from django.forms.widgets import ClearableFileInput

from etruekko.truekko.models import UserProfile
from etruekko.truekko.models import Group
from etruekko.truekko.models import User
from etruekko.truekko.models import Membership
from etruekko.truekko.models import Transfer
from etruekko.truekko.models import Item
from etruekko.truekko.models import Tag
from etruekko.truekko.models import ItemTagged
from etruekko.truekko.models import WallMessage
from etruekko.truekko.models import Commitment
from etruekko.truekko.models import PostalAddress

from etruekko.globaltags.tags import tooltip


class CustomImageWidget(ClearableFileInput):

    template_with_initial = u'%(clear_template)s<br />%(input_text)s: %(input)s'


class UserProfileForm(ModelForm):
    required_css_class = 'required'
    email = forms.EmailField()

    class Meta:
        model = UserProfile
        fields = ('photo', 'name', 'email', 'location', 'web', 'description', 'receive_notification')
        widgets = {'photo': CustomImageWidget()}

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = self.instance.user.email

    def save(self):
        instance = super(UserProfileForm, self).save(commit=False)
        instance.user.email = self.cleaned_data['email']
        instance.user.save()
        instance.save()


class GroupForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Group
        fields = ('photo', 'name', 'location', 'web', 'description')
        widgets = {'photo': CustomImageWidget()}


class RegisterForm(forms.Form):
    required_css_class = 'required'

    username = forms.CharField(label=_("Username"))
    name = forms.CharField(label=_("Name"))
    location = forms.CharField(label=_("Location"))
    email = forms.EmailField(label=_("Email"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirm"), widget=forms.PasswordInput)
    accept_terms = forms.BooleanField(label=_("I accept"),
                                      help_text=_('You should accept '
                                      'the <a href="/terms">terms of use</a> '
                                      'and the <a href="/privacy">privacy policy</a> '
                                      'to join to etruekko'),
                                      error_messages={'required': _("You should accept the terms of use and the privacy policy")},
                                      required=True)

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if not re.match("^\w+$", username):
            raise forms.ValidationError(_("Username isn't valid, use only letters, numbers or _"))

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
        p.location = data["location"]
        p.save()

        m = Membership(user=u, group=group, role="REQ")
        m.save()


class TransferDirectForm(forms.Form):
    required_css_class = 'required'

    concept = forms.CharField(label=_("Concept"), max_length=500)
    credits = forms.IntegerField(label=_("Credits"))

    def __init__(self, user_from, user_to, *args, **kwargs):
        self.user_from = user_from
        self.user_to = user_to
        super(TransferDirectForm, self).__init__(*args, **kwargs)

    def clean_credits(self):
        credits = self.cleaned_data.get('credits')
        if credits < 0:
            raise forms.ValidationError(_("Can't make this transfer, negative credits isn't allowed"))
        if credits > self.user_from.get_profile().credits:
            raise forms.ValidationError(_("Can't make this transfer, insufficient credits"))

        return credits

    def save(self):
        data = self.cleaned_data
        t = Transfer(user_from=self.user_from,
                     user_to=self.user_to,
                     credits=data['credits'],
                     concept=data['concept'])
        t.save()


class ItemAddForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Item
        fields = ('name', 'type', 'offer_or_demand', 'description', 'photo', 'price', 'price_type')
        widgets = {'photo': CustomImageWidget()}

    def quantity(self):
        return self.instance.quantity


class WallMessageForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = WallMessage
        fields = ('msg', 'private')


class ContactForm(forms.Form):
    required_css_class = 'required'

    sender = forms.EmailField(label=_("Email"))
    subject = forms.CharField(label=_("Subject"), max_length=100)
    phone = forms.CharField(label=_("Phone"), required=False, max_length=100)
    message = forms.CharField(label=_("Message"), widget=forms.Textarea)
    cc_myself = forms.BooleanField(label=_("Send a copy to myself"), required=False)

    def send(self):
        subject = self.cleaned_data['subject']
        message = self.cleaned_data['message']
        sender = self.cleaned_data['sender']
        phone = self.cleaned_data['phone']
        cc_myself = self.cleaned_data['cc_myself']

        msg = _("Phone: %(number)s\n\n%(msg)s") % dict(number=phone, msg=message)
        recipients = ['info@etruekko.com']
        if cc_myself:
            recipients.append(sender)

        from django.core.mail import send_mail
        send_mail(subject, msg, sender, recipients)


class CommitmentForm(ModelForm):
    required_css_class = 'required'

    #def __init__(self, users, *args, **kwargs):
    #    super(CommitmentForm, self).__init__(*args, **kwargs)
    #    self.fields['user_from'].queryset = User.objects.filter(pk__in=users)
    #    self.fields['user_to'].queryset = User.objects.filter(pk__in=users)

    class Meta:
        model = Commitment
        #fields = ('user_from', 'user_to', 'comment')
        fields = ('comment', )


class PostalForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = PostalAddress
        exclude = ('user',)
