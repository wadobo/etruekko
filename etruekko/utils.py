from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.conf import settings


COLORS = {
    'home': '#23B0DF',
    'people': '#A85F96',
    'serv': '#BC4484',
    'item': '#E36D9D',
    'add': '#DC4D54',
    'transf': '#E6E06F',
    'msg': '#94B665',
}


def context_processor(request):
    '''
    This is a context processor that adds some vars to the base template
    '''

    return {
        'MEDIA_URL': settings.MEDIA_URL,
        'SITE_NAME': settings.SITE_NAME,
        'COLORS': COLORS,
        'USER': request.user,
    }


def paginate(request, queryset, n=10):
    paginator = Paginator(queryset, n)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        p = paginator.page(page)
    except (EmptyPage, InvalidPage):
        p = paginator.page(paginator.num_pages)

    return p
