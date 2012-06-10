from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from etruekko.truekko.models import Membership
from etruekko.truekko.models import User
from etruekko.truekko.models import Group


def has_perm(view, test_function, message="", next="/"):

    def new_func(request, *args, **kwargs):
        if test_function(request, *args, **kwargs):
            return view(request, *args, **kwargs)
        else:
            if not message:
                message = _("Sorry but you don't have permission")

            messages.info(request, message)
            return redirect('/')

    return new_func


def is_group_admin(view):

    def new_func(request, groupid):
        if is_group_editable(request.user.username, groupid):
            return view(request, groupid)
        else:
            message = _("Only community admin can edit this community")
            messages.info(request, message)
            return redirect('view_group', groupid)

    return new_func


def is_group_editable(username, groupid):
    try:
        user = User.objects.get(username=username)
        m = user.membership_set.get(group__pk=groupid)
    except:
        return False

    return m.role == "ADM"


def is_member(user, group):
    try:
        n = user.membership_set.filter(group=group, role__in=["MEM", "ADM"]).count()
    except:
        return False

    return bool(n)
