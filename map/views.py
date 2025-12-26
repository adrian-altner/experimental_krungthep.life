from django.shortcuts import render
from django.utils.html import escape


def transport_map(request):
    lat = request.GET.get("lat")
    lng = request.GET.get("lng")
    title = request.GET.get("title") or "Station"
    system = request.GET.get("system") or ""
    line = request.GET.get("line") or ""

    map_points = []
    if lat and lng:
        try:
            lat_value = float(lat)
            lng_value = float(lng)
        except ValueError:
            lat_value = None
            lng_value = None
        if lat_value is not None and lng_value is not None:
            subtitle = " · ".join(filter(None, [system, line]))
            map_points.append(
                {
                    "lat": lat_value,
                    "lng": lng_value,
                    "title": escape(title),
                    "subtitle": escape(subtitle),
                }
            )

    return render(
        request,
        "map/transport_map.html",
        {
            "map_points": map_points,
            "title": title,
        },
    )
