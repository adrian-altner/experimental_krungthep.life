from typing import cast

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
    pages = site.root_page.get_children().live().in_menu()
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
