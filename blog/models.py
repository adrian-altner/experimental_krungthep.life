from django.db import models

# Add these:
from wagtail.models import Page
from wagtail import blocks
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock


class BlogPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + ["intro"]
    template = "blog/blog_page.html"


class BlogPost(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title")),
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
        ],
        blank=True,
        use_json_field=True,
    )

    content_panels = Page.content_panels + ["date", "intro", "body"]
    template = "blog/blog_post.html"
