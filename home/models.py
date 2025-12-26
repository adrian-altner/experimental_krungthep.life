from django.db import models

from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page


class HomePage(Page):
    subpage_types = ["home.AboutPage", "home.BlankPage"]


class AboutPage(Page):
    rich_text_features = [
        "h2",
        "h3",
        "h4",
        "bold",
        "italic",
        "link",
        "ol",
        "ul",
    ]
    intro = StreamField(
        [
            ("paragraph", blocks.RichTextBlock(features=rich_text_features)),
        ],
        blank=True,
        use_json_field=True,
    )
    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title")),
            ("paragraph", blocks.RichTextBlock(features=rich_text_features)),
            ("image", ImageChooserBlock()),
            ("embed", EmbedBlock()),
            ("document", DocumentChooserBlock()),
        ],
        blank=True,
        use_json_field=True,
    )
    summary = models.TextField(blank=True)
    reading_time = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Estimated reading time in minutes.",
    )
    featured = models.BooleanField(default=False)
    publish_date = models.DateField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
        FieldPanel("summary"),
        FieldPanel("reading_time"),
        FieldPanel("featured"),
        FieldPanel("publish_date"),
    ]
    promote_panels = Page.promote_panels + [
        FieldPanel("seo_title"),
        FieldPanel("search_description"),
    ]
    parent_page_types = ["home.HomePage"]
    subpage_types = []


class BlankPage(Page):
    rich_text_features = [
        "h2",
        "h3",
        "h4",
        "bold",
        "italic",
        "link",
        "ol",
        "ul",
    ]
    intro = StreamField(
        [
            ("paragraph", blocks.RichTextBlock(features=rich_text_features)),
        ],
        blank=True,
        use_json_field=True,
    )
    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title")),
            ("paragraph", blocks.RichTextBlock(features=rich_text_features)),
            ("image", ImageChooserBlock()),
            ("embed", EmbedBlock()),
            ("document", DocumentChooserBlock()),
        ],
        blank=True,
        use_json_field=True,
    )
    summary = models.TextField(blank=True)
    reading_time = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Estimated reading time in minutes.",
    )
    featured = models.BooleanField(default=False)
    publish_date = models.DateField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
        FieldPanel("summary"),
        FieldPanel("reading_time"),
        FieldPanel("featured"),
        FieldPanel("publish_date"),
    ]
    promote_panels = Page.promote_panels + [
        FieldPanel("seo_title"),
        FieldPanel("search_description"),
    ]
    parent_page_types = ["home.HomePage"]
    subpage_types = []
    template = "home/blank_page.html"
