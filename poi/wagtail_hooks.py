from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _

from wagtail import hooks
from wagtail.admin.menu import MenuItem

from poi.admin_views import poi_index_list


@hooks.register("register_admin_menu_item")
def register_poi_menu_item():
    return MenuItem(
        _("POI"),
        reverse("poi_index_list"),
        icon_name="site",
        order=220,
    )


@hooks.register("register_admin_urls")
def register_poi_admin_urls():
    return [
        path("poi/", poi_index_list, name="poi_index_list"),
    ]
