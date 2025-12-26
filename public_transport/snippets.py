from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from public_transport.models import TransportStation


class TransportStationViewSet(SnippetViewSet):
    model = TransportStation
    list_display = (  # type: ignore[reportIncompatibleVariableOverride]
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
    list_filter = (  # type: ignore[reportIncompatibleVariableOverride]
        "system_label",
        "line_label",
        "opening",
        "created_at",
        "updated_at",
    )
    search_fields = (  # type: ignore[reportIncompatibleVariableOverride]
        "station_label",
        "system_label",
        "line_label",
        "station_codes",
        "station_qid",
        "line_qid",
    )
    ordering = ["station_label", "line_label"]  # type: ignore[reportIncompatibleVariableOverride]


register_snippet(TransportStationViewSet)
