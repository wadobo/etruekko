from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

def generate_menu(selected=''):
    menu = (
        ("home", _("Home"), reverse("index"), selected == "home"),
        ("people", _("People"), reverse("people"), selected == "people"),
        ("serv", _("Services"), reverse("item_list", args=('serv',)), selected == "serv"),
        ("item", _("Item"), reverse("item_list", args=('item',)), selected == "item"),
        ("add", _("Add"), reverse("item_add"), selected == "add"),
        ("transf", _("Transf"), reverse("transfer_list"), selected == "transf"),
        ("msg", _("Messages"), "", selected == "msgs"),
        ("group", _("Groups"), reverse("groups"), selected == "group"),
    )

    return menu
