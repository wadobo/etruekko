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
def gravatar(email, size=48, d='identicon'):
    gravatar_url = "http://www.gravatar.com/avatar.php?"
    gravatar_url += urllib.urlencode({
        'gravatar_id': hashlib.md5(email.lower()).hexdigest(),
        'size': str(size),
        'd': d})
    return gravatar_url
