from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

def generate_menu(selected=''):
    menu = (
        ("home", _("Home"), reverse("index"), selected == "home"),
        ("people", _("People"), "", selected == "people"),
        ("serv", _("Services"), "", selected == "serv"),
        ("item", _("Item"), "", selected == "item"),
        ("add", _("Add"), "", selected == "add"),
        ("transf", _("Transf"), "", selected == "tranfs"),
        ("msg", _("Messages"), "", selected == "msgs"),
    )

    return menu
