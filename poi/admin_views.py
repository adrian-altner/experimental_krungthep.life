from django.shortcuts import render
from django.urls import reverse

from wagtail.admin.auth import permission_denied, user_has_any_page_permission

from poi.models import POIIndexPage


def poi_index_list(request):
    if not user_has_any_page_permission(request.user):
        return permission_denied(request)

    indexes = POIIndexPage.objects.live().order_by("title")
    data = []
    for page in indexes:
        data.append(
            {
                "title": page.title,
                "category": page.category.title if page.category else "All categories",
                "explore_url": reverse("wagtailadmin_explore", args=[page.id]),
                "add_poi_url": reverse(
                    "wagtailadmin_pages:add", args=["poi", "poipage", page.id]
                ),
            }
        )

    return render(
        request,
        "poi/admin/poi_index_list.html",
        {
            "indexes": data,
        },
    )
