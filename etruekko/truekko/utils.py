from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

def generate_menu(selected=''):
    menu = (
        ("home", _("Wall"), reverse("index"), selected == "home"),
        ("people", _("My contacts"), reverse("people"), selected == "people"),
        ("serv", _("Services"), reverse("item_list", args=('serv',)), selected == "serv"),
        ("item", _("Item"), reverse("item_list", args=('item',)), selected == "item"),
        ("add", _("Create your offerts and demands"), reverse("item_add"), selected == "add"),
        ("transf", _("My swaps"), reverse("transfer_list"), selected == "transf"),
        ("group", _("My groups"), reverse("groups"), selected == "group"),
    )

    return menu
