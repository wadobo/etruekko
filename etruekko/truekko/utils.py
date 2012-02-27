from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

def generate_menu(selected=''):
    menu = (
        ("home", _("Home"), reverse("index"), selected == "home"),
        ("people", _("People"), reverse("people"), selected == "people"),
        ("serv", _("Services"), "", selected == "serv"),
        ("item", _("Item"), "", selected == "item"),
        ("add", _("Add"), "", selected == "add"),
        ("transf", _("Transf"), reverse("transfer_list"), selected == "transf"),
        ("msg", _("Messages"), "", selected == "msgs"),
        ("group", _("Groups"), reverse("groups"), selected == "group"),
    )

    return menu
