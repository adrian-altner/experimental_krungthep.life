from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from public_transport.models import TransportStation


class TransportStationViewSet(SnippetViewSet):
    model = TransportStation
    list_display = (
        "station_label",
        "system_label",
        "line_label",
        "station_codes",
        "opening",
        "created_at",
        "updated_at",
        "latitude",
        "longitude",
        "station_qid",
        "line_qid",
    )
    list_filter = ("system_label", "line_label", "opening", "created_at", "updated_at")
    search_fields = (
        "station_label",
        "system_label",
        "line_label",
        "station_codes",
        "station_qid",
        "line_qid",
    )
    ordering = ["station_label", "line_label"]


register_snippet(TransportStationViewSet)
