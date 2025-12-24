from django.db import models

from wagtail.fields import RichTextField
from wagtail.models import Page


class HomePage(Page):
    pass


class AboutPage(Page):
    intro = RichTextField(blank=True)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + ["intro", "body"]
    parent_page_types = ["home.HomePage"]
    subpage_types = []
