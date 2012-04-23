import os
import Image
from django import template
import urllib, hashlib
from django.conf import settings


register = template.Library()

@register.simple_tag
def avatar(user, size=48):
    puser = user.get_profile()
    if(puser.photo):
        path = puser.photo.path
        path = "%s_%s.png" % (path, size)
        if not os.path.exists(path):
            im = Image.open(puser.photo.path)
            im.thumbnail((size, size))
            im.save(path)

        path = path[len(settings.MEDIA_ROOT) + 1:]
        return settings.MEDIA_URL + path
    else:
        return gravatar(user.email, size)


@register.simple_tag
def image(img, size=48):
    path = img.path
    path = "%s_%s.png" % (path, size)
    if not os.path.exists(path):
        im = Image.open(img.path)
        im.thumbnail((size, size))
        im.save(path)

    path = path[len(settings.MEDIA_ROOT) + 1:]
    return settings.MEDIA_URL + path


@register.simple_tag
def groupavatar(group, size=48):
    if(group.photo):
        path = group.photo.path
        path = "%s_%s.png" % (path, size)
        if not os.path.exists(path):
            im = Image.open(group.photo.path)
            im.thumbnail((size, size))
            im.save(path)

        path = path[len(settings.MEDIA_ROOT) + 1:]
        return settings.MEDIA_URL + path
    else:
        return gravatar(group.email, size)


@register.simple_tag
def gravatar(email, size=48, d='identicon'):
    gravatar_url = "http://www.gravatar.com/avatar.php?"
    gravatar_url += urllib.urlencode({
        'gravatar_id': hashlib.md5(email.lower()).hexdigest(),
        'size': str(size),
        'd': d})
    return gravatar_url


@register.inclusion_tag("user_rating.html",\
    takes_context=True)
def user_rating(context, user):
    '''
    Renders actions for a given service if any. Assumes user is authenticated
    '''
    return {'user': context['user'], "profile": user.get_profile()}

@register.simple_tag(takes_context=True)
def is_admin_group(context, user, group):
    context['is_admin_group_v'] = group.is_admin(user)
    return ''


@register.inclusion_tag("clear.html", takes_context=True)
def clear_mod_3(context):
    mod3 = context.get('forloop').get('counter') % 3
    return {'mod3': mod3}
