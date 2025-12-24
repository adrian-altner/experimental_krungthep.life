from typing import Any, cast

from django import template
from django.conf import settings
from wagtail.models import Page, Site

register = template.Library()


@register.simple_tag(takes_context=True)
def primary_menu(context):
    request = context.get("request")
    site = Site.find_for_request(request) if request else None
    if not site:
        return Page.objects.none()

    site = cast(Site, site)
    root_page = site.root_page
    nav_page_id = getattr(settings, "NAVIGATION_ROOT_PAGE_ID", None)
    nav_slug = getattr(settings, "NAVIGATION_ROOT_SLUG", None)
    if nav_page_id:
        root_page = Page.objects.filter(id=nav_page_id).first() or root_page
    elif nav_slug:
        scoped_root = root_page.get_descendants().filter(slug=nav_slug).first()
        if scoped_root:
            root_page = scoped_root

    pages = cast(Any, root_page.get_children()).live().in_menu()
    for item in getattr(settings, "NAV_EXCLUDE_MODELS", []):
        try:
            app_label, model = item.split(".", 1)
        except ValueError:
            continue
        pages = pages.exclude(
            content_type__app_label=app_label,
            content_type__model=model,
        )
    return pages
