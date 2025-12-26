from django import forms
from django.apps import apps
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.http import Http404
from django.db import models
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index
from wagtail.url_routing import RouteResult

from public_transport.panels import ParentLinePanel
from django.utils.text import slugify

class PublicTransportIndexPageForm(WagtailAdminPageForm):
    system_filters = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        TransportStation = apps.get_model("public_transport", "TransportStation")
        systems = (
            TransportStation.objects.exclude(system_label="")
            .values_list("system_label", flat=True)
            .distinct()
            .order_by("system_label")
        )
        self.fields["system_filters"].choices = [(s, s) for s in systems]
        if self.instance and self.instance.system_filters:
            self.fields["system_filters"].initial = self.instance.system_filters

    def clean_system_filters(self):
        return self.cleaned_data["system_filters"]


class PublicTransportStationPageForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        parent_page = kwargs.get("parent_page")
        super().__init__(*args, **kwargs)
        if "parent_line_display" in self.fields:
            self.fields["parent_line_display"].disabled = True
        TransportStation = apps.get_model("public_transport", "TransportStation")
        queryset = TransportStation.objects.all()
        parent = parent_page or self.parent_page or (
            self.instance.get_parent() if self.instance.pk else None
        )
        if parent:
            parent = parent.specific
            if getattr(parent, "title", None) and "parent_line_display" in self.fields:
                self.fields["parent_line_display"].initial = parent.title
                self.instance.parent_line_display = parent.title
            line_label = getattr(parent, "line_label", None)
            line_qid = getattr(parent, "line_qid", None)
            system_label = getattr(parent, "system_label", None)
            if line_qid:
                queryset = queryset.filter(line_qid=line_qid)
            elif line_label:
                queryset = queryset.filter(line_label=line_label)
            if system_label:
                queryset = queryset.filter(system_label=system_label)
        if "station" in self.fields:
            self.fields["station"] = forms.ModelChoiceField(
                queryset=queryset.order_by("station_label"),
                required=False,
                label="Station",
            )


class PublicTransportIndexPage(Page):
    intro = RichTextField(blank=True)
    system_filters = models.JSONField(default=list, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("system_filters"),
    ]
    parent_page_types = ["home.HomePage"]
    subpage_types = [
        "public_transport.PublicTransportSystemPage",
    ]
    base_form_class = PublicTransportIndexPageForm

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["system_pages"] = PublicTransportSystemPage.objects.child_of(
            self
        ).live()
        return context


class PublicTransportSystemPage(Page):
    intro = RichTextField(blank=True)
    system_label = models.CharField(max_length=200)
    system_qid = models.CharField(max_length=40, blank=True)
    show_stations = models.BooleanField(
        default=False,
        help_text="Show stations directly on this system page instead of lines.",
    )
    station_sort = models.CharField(
        max_length=40,
        default="station_label",
        choices=[
            ("station_label", "Station name (A-Z)"),
            ("-station_label", "Station name (Z-A)"),
            ("opening", "Opening date (oldest first)"),
            ("-opening", "Opening date (newest first)"),
            ("line_label", "Line (A-Z)"),
            ("station_codes", "Station code (A-Z)"),
        ],
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel(
            [
                FieldPanel("system_label"),
                FieldPanel("system_qid"),
                FieldPanel("show_stations"),
                FieldPanel("station_sort"),
            ],
            heading="System",
        ),
    ]
    parent_page_types = ["public_transport.PublicTransportIndexPage"]
    subpage_types = ["public_transport.PublicTransportLinePage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["line_pages"] = self.get_children().live().specific()
        if self.show_stations:
            sort_key = self.station_sort or "station_label"
            stations = TransportStation.objects.filter(
                system_label=self.system_label
            ).order_by(sort_key)
            context["station_cards"] = build_station_cards(stations, parent_page=self)
        return context

    def route(self, request, path_components):
        if not path_components:
            return super().route(request, path_components)

        try:
            return super().route(request, path_components)
        except Http404:
            if self.show_stations and len(path_components) == 1:
                station_slug = path_components[0]
                station_page = (
                    PublicTransportStationPage.objects.descendant_of(self)
                    .live()
                    .filter(slug=station_slug)
                    .first()
                )
                if station_page:
                    return RouteResult(station_page)
            raise


class PublicTransportLinePage(Page):
    intro = RichTextField(blank=True)
    line_label = models.CharField(max_length=200)
    line_qid = models.CharField(max_length=40, blank=True)
    system_label = models.CharField(max_length=200, blank=True)
    station_sort = models.CharField(
        max_length=40,
        default="station_label",
        choices=[
            ("station_label", "Station name (A-Z)"),
            ("-station_label", "Station name (Z-A)"),
            ("opening", "Opening date (oldest first)"),
            ("-opening", "Opening date (newest first)"),
            ("station_codes", "Station code (A-Z)"),
        ],
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel(
            [
                FieldPanel("line_label"),
                FieldPanel("line_qid"),
                FieldPanel("system_label"),
                FieldPanel("station_sort"),
            ],
            heading="Line",
        ),
    ]
    parent_page_types = ["public_transport.PublicTransportSystemPage"]
    subpage_types = ["public_transport.PublicTransportStationPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        stations = TransportStation.objects.filter(
            system_label=self.system_label,
            line_label=self.line_label,
        ).order_by(self.station_sort or "station_label")
        context["station_cards"] = build_station_cards(stations, parent_page=self)
        return context


class PublicTransportStationPage(Page):
    station = models.ForeignKey(
        "public_transport.TransportStation",
        on_delete=models.PROTECT,
        related_name="station_pages",
        blank=True,
        null=True,
    )
    intro = RichTextField(blank=True)
    body = RichTextField(blank=True)
    parent_line_display = models.CharField(max_length=200, blank=True)

    content_panels = Page.content_panels + [
        ParentLinePanel(),
        FieldPanel("station"),
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    parent_page_types = [
        "public_transport.PublicTransportLinePage",
        "public_transport.PublicTransportSystemPage",
    ]
    subpage_types = []
    base_form_class = PublicTransportStationPageForm

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["station"] = self.station
        parent = self.get_parent().specific if self.get_parent() else None
        context["parent_line"] = parent if isinstance(parent, PublicTransportLinePage) else None
        context["parent_system"] = parent if isinstance(parent, PublicTransportSystemPage) else None
        return context

    def clean(self):
        super().clean()
        parent = self.get_parent().specific if self.get_parent() else None
        if isinstance(parent, PublicTransportLinePage):
            self.parent_line_display = parent.title
        if isinstance(parent, PublicTransportSystemPage) and not parent.show_stations:
            raise ValidationError(
                {"__all__": "This system page is not set to show stations."}
            )
        if self.station:
            previous_label = ""
            if self.pk:
                previous = PublicTransportStationPage.objects.filter(pk=self.pk).first()
                if previous and previous.station:
                    previous_label = previous.station.station_label
            if not self.title or self.title == previous_label:
                self.title = self.station.station_label
                if not self.slug:
                    self.slug = slugify(self.title) or self.slug


class TransportStation(index.Indexed, models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    station_label = models.CharField(max_length=200)
    station_qid = models.CharField(max_length=40, blank=True)
    system_label = models.CharField(max_length=200, blank=True)
    system_qid = models.CharField(max_length=40, blank=True)
    line_label = models.CharField(max_length=200, blank=True)
    line_qid = models.CharField(max_length=40, blank=True)
    opening = models.DateField(blank=True, null=True)
    station_codes = models.CharField(max_length=120, blank=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    raw_properties = models.JSONField(default=dict, blank=True)

    panels = [
        FieldPanel("station_label"),
        MultiFieldPanel(
            [
                FieldPanel("station_qid"),
                FieldPanel("station_codes"),
                FieldPanel("opening"),
            ],
            heading="Station",
        ),
        MultiFieldPanel(
            [
                FieldPanel("system_label"),
                FieldPanel("system_qid"),
                FieldPanel("line_label"),
                FieldPanel("line_qid"),
            ],
            heading="Line & system",
        ),
        MultiFieldPanel(
            [
                FieldPanel("latitude"),
                FieldPanel("longitude"),
            ],
            heading="Coordinates",
        ),
        FieldPanel("raw_properties"),
    ]

    search_fields = [
        index.SearchField("station_label", partial_match=True),
        index.SearchField("system_label", partial_match=True),
        index.SearchField("line_label", partial_match=True),
        index.FilterField("station_qid"),
        index.FilterField("line_qid"),
    ]

    class Meta:
        ordering = ["station_label", "line_label"]
        constraints = [
            models.UniqueConstraint(
                fields=["station_qid", "line_qid"],
                name="unique_station_per_line",
            ),
        ]

    def __str__(self):
        label = self.station_label
        if self.line_label:
            return f"{label} ({self.line_label})"
        return label


def build_station_cards(stations, parent_page=None):
    pages = PublicTransportStationPage.objects.filter(
        station__in=stations
    ).select_related("station")
    page_map = {page.station_id: page for page in pages if page.station_id}
    if parent_page:
        scoped_pages = pages.child_of(parent_page)  # type: ignore[attr-defined]
        scoped_map = {page.station_id: page for page in scoped_pages if page.station_id}
    else:
        scoped_map = {}
    cards = []
    for station in stations:
        page = scoped_map.get(station.id) or page_map.get(station.id)
        page_url = page.url if page else None
        if (
            page
            and parent_page
            and isinstance(parent_page, PublicTransportSystemPage)
            and parent_page.show_stations
        ):
            page_url = f"{parent_page.url}{page.slug}/"
        cards.append(
            {
                "station": station,
                "page_url": page_url,
            }
        )
    return cards
