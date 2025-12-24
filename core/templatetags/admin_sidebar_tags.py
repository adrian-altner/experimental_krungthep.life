from django import template
from django.urls import reverse
from django.utils.html import json_script
from django.utils.translation import gettext_lazy as _

from wagtail.admin.menu import admin_menu
from wagtail.admin.search import admin_search_areas
from wagtail.admin.telepath import JSContext
from wagtail.admin.ui import sidebar

register = template.Library()


@register.simple_tag(takes_context=True)
def custom_sidebar_props(context):
    request = context["request"]
    search_areas = admin_search_areas.search_items_for_request(request)
    search_area = search_areas[0] if search_areas else None

    account_menu = [
        sidebar.LinkMenuItem(
            "account", _("Account"), reverse("wagtailadmin_account"), icon_name="user"
        ),
        sidebar.ActionMenuItem(
            "logout", _("Log out"), reverse("wagtailadmin_logout"), icon_name="logout"
        ),
    ]

    modules = [
        sidebar.SearchModule(search_area) if search_area else None,
        sidebar.MainMenuModule(
            admin_menu.render_component(request), account_menu, request.user
        ),
    ]
    modules = [module for module in modules if module is not None]

    return json_script(
        {
            "modules": JSContext().pack(modules),
        },
        element_id="wagtail-sidebar-props",
    )
