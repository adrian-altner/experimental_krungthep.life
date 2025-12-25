from urllib.parse import urlencode

from django import forms
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify
from django.db import models
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.images.models import Image
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet


@register_snippet
class POICategory(index.Indexed, models.Model):
    title = models.CharField(max_length=120)
    sort_order = models.PositiveIntegerField(default=0)

    panels = [
        FieldPanel("title"),
        FieldPanel("sort_order"),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
    ]

    class Meta:
        ordering = ["sort_order", "title"]
        verbose_name = "POI Category"
        verbose_name_plural = "POI Categories"

    def __str__(self):
        return self.title


@register_snippet
class POIFeature(index.Indexed, models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, max_length=80)
    group = models.CharField(max_length=120, blank=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("slug"),
        FieldPanel("group"),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
        index.FilterField("slug"),
        index.FilterField("group"),
    ]

    class Meta:
        ordering = ["group", "title"]

    def __str__(self):
        return self.title


class POIPage(Page):
    category = models.ForeignKey(
        POICategory,
        on_delete=models.PROTECT,
        related_name="poi_pages",
    )
    short_description = models.TextField()
    full_description = RichTextField(blank=True)
    features = ParentalManyToManyField(POIFeature, blank=True, related_name="poi_pages")

    address = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=120, blank=True, default="Bangkok")
    country = models.CharField(max_length=120, blank=True, default="Thailand")
    landmark = models.CharField(max_length=120, blank=True)
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

    website = models.URLField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)

    hero_image = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    verified = models.BooleanField(default=False)
    price_level = models.CharField(max_length=30, blank=True)
    editor_notes = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("category"),
                FieldPanel("short_description"),
                FieldPanel("full_description"),
                FieldPanel("features", widget=forms.CheckboxSelectMultiple),
            ],
            heading="Identity & classification",
        ),
        MultiFieldPanel(
            [
                FieldPanel("address"),
                FieldPanel("district"),
                FieldPanel("city"),
                FieldPanel("country"),
                FieldPanel("landmark"),
                FieldPanel("latitude"),
                FieldPanel("longitude"),
            ],
            heading="Location",
        ),
        MultiFieldPanel(
            [
                FieldPanel("website"),
                FieldPanel("phone"),
                FieldPanel("instagram_url"),
                FieldPanel("facebook_url"),
            ],
            heading="Contact",
        ),
        MultiFieldPanel(
            [
                FieldPanel("hero_image"),
                InlinePanel("gallery_images", label="Gallery images"),
            ],
            heading="Media",
        ),
        MultiFieldPanel(
            [
                FieldPanel("verified"),
                FieldPanel("price_level"),
                FieldPanel("editor_notes"),
            ],
            heading="Quality & editorial",
        ),
    ]

    parent_page_types = ["poi.POIIndexPage"]
    subpage_types = []

    search_fields = Page.search_fields + [
        index.SearchField("title", partial_match=True),
        index.SearchField("short_description", partial_match=True),
        index.SearchField("full_description"),
        index.SearchField("address"),
        index.RelatedFields(
            "category",
            [
                index.SearchField("title", partial_match=True),
                index.FilterField("slug"),
            ],
        ),
    ]

    class Meta:
        verbose_name = "POI"


class POIPageGalleryImage(Orderable):
    page = ParentalKey(POIPage, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        related_name="+",
    )
    caption = models.CharField(max_length=250, blank=True)

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]


class POIIndexPage(Page):
    intro = RichTextField(blank=True)
    category = models.ForeignKey(
        POICategory,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="poi_indexes",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("category"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["poi.POIPage"]

    def clean(self):
        if self.category:
            self.slug = slugify(self.category.title)
        elif self.title:
            self.slug = slugify(self.title)

        if self.category:
            existing = (
                POIIndexPage.objects.filter(category=self.category)
                .exclude(id=self.id)
                .exists()
            )
            if existing:
                raise ValidationError(
                    {"category": "This category is already used by another POI index page."}
                )

        super().clean()

    def save(self, *args, **kwargs):
        if self.category:
            self.slug = slugify(self.category.title)
        elif self.title:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_filtered_pois(self, request):
        pois = (
            POIPage.objects.child_of(self)
            .live()
            .select_related("category", "hero_image")
            .prefetch_related("features", "gallery_images__image")
            .order_by("title")
        )

        fixed_category_id = self.category_id
        selected_category = request.GET.get("category") or ""
        if fixed_category_id:
            selected_category = str(fixed_category_id)
        selected_features = request.GET.getlist("feature")
        search_query = request.GET.get("q") or ""
        verified_only = request.GET.get("verified") == "1"

        if fixed_category_id:
            pois = pois.filter(category_id=fixed_category_id)
        elif selected_category:
            pois = pois.filter(category_id=selected_category)
        if selected_features:
            pois = pois.filter(features__slug__in=selected_features).distinct()
        if verified_only:
            pois = pois.filter(verified=True)
        if search_query:
            pois = pois.search(search_query)

        return pois, selected_category, selected_features, search_query, verified_only

    def build_context(self, request):
        context = super().get_context(request)
        pois, selected_category, selected_features, search_query, verified_only = (
            self.get_filtered_pois(request)
        )

        map_pois = [
            {
                "title": poi.title,
                "category": poi.category.title,
                "url": poi.url,
                "lat": float(poi.latitude),
                "lng": float(poi.longitude),
            }
            for poi in pois
            if poi.latitude is not None and poi.longitude is not None
        ]

        page_number = request.GET.get("page", 1)
        paginator = Paginator(pois, 12)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        query_params = request.GET.copy()
        query_params.pop("page", None)
        querystring = urlencode(query_params, doseq=True)

        selected_category_obj = self.category
        if not selected_category_obj and selected_category:
            selected_category_obj = POICategory.objects.filter(id=selected_category).first()

        context.update(
            {
                "pois": page_obj.object_list,
                "page_obj": page_obj,
                "categories": POICategory.objects.all(),
                "features": POIFeature.objects.all(),
                "selected_category": selected_category,
                "selected_category_obj": selected_category_obj,
                "is_category_locked": bool(self.category),
                "selected_features": selected_features,
                "search_query": search_query,
                "verified_only": verified_only,
                "map_pois": map_pois,
                "querystring": querystring,
            }
        )
        return context

    def get_context(self, request, *args, **kwargs):
        return self.build_context(request)
