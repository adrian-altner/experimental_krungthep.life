import math
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django import forms
from django.db import models
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils.html import strip_tags
from django.utils.text import slugify
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import Tag, TaggedItemBase
from wagtail import blocks
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.snippets.models import register_snippet
from core.image_utils import assign_page_images


@register_snippet
class BlogCategory(models.Model):
    title = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, unique=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("slug"),
    ]

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class BlogPostTag(TaggedItemBase):
    content_object = ParentalKey(
        "blog.BlogPost",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


class BlogPage(RoutablePageMixin, Page):
    content_panels = Page.content_panels
    parent_page_types = ["home.HomePage"]
    subpage_types = ["blog.BlogPost"]
    template = "blog/blog_page.html"

    def get_base_posts(self):
        return BlogPost.objects.child_of(self).live()  # type: ignore[attr-defined]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        all_posts = self.get_base_posts()
        posts = all_posts.order_by("-published_date")
        tag_slug = request.GET.get("tag")
        category_slug = request.GET.get("category")
        author_slug = request.GET.get("author")
        if tag_slug:
            posts = posts.filter(tags__slug=tag_slug)
        if category_slug:
            posts = posts.filter(category__slug=category_slug)
        if author_slug:
            posts = posts.filter(author__author_slug=author_slug)
        context["posts"] = posts
        context["active_tag"] = tag_slug
        context["active_category"] = category_slug
        context["active_author"] = author_slug
        context["categories"] = (
            BlogCategory.objects.filter(blog_posts__in=all_posts)
            .distinct()
            .order_by("title")
        )
        User = get_user_model()
        context["authors"] = (
            User.objects.filter(blog_posts__in=all_posts)
            .distinct()
            .order_by("first_name", "last_name", "email")
        )
        context["tags"] = (
            Tag.objects.filter(blog_blogposttag_items__content_object__in=all_posts)
            .distinct()
            .order_by("name")
        )
        return context

    def get_author_base_queryset(self):
        User = get_user_model()
        return (
            User.objects.filter(blog_posts__in=self.get_base_posts())
            .exclude(author_slug__isnull=True)
            .exclude(author_slug="")
            .distinct()
        )

    def serve(self, request, *args, **kwargs):
        if request.headers.get("HX-Request") == "true":
            context = self.get_context(request, *args, **kwargs)
            return TemplateResponse(request, "blog/_blog_results.html", context)
        return super().serve(request, *args, **kwargs)

    @route(r"^authors/$")
    def author_index(self, request):
        context = self.get_context(request)
        context["authors"] = self.get_author_base_queryset().order_by(
            "first_name", "last_name", "email"
        )
        return self.render(
            request,
            context_overrides=context,
            template="blog/author_index.html",
        )

    @route(r"^authors/(?P<author_slug>[-a-zA-Z0-9_]+)/$")
    def author_detail(self, request, author_slug):
        User = get_user_model()
        author = (
            self.get_author_base_queryset()
            .filter(author_slug=author_slug)
            .first()
        )
        if not author:
            raise Http404
        posts = self.get_base_posts().filter(author=author).order_by("-published_date")
        context = self.get_context(request)
        context["author"] = author
        context["posts"] = posts
        return self.render(
            request,
            context_overrides=context,
            template="blog/author_detail.html",
        )


class BlogPostForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if (
            not self.is_bound
            and self.for_user
            and "author" in self.fields
            and not self.instance.author_id
        ):
            self.fields["author"].initial = self.for_user.pk
        if (
            not self.is_bound
            and "category" in self.fields
            and not self.instance.category_id
        ):
            try:
                default_category = BlogCategory.objects.get(slug="general")
            except BlogCategory.DoesNotExist:
                default_category = None
            if default_category:
                self.fields["category"].initial = default_category.pk


class BlogPost(Page):
    base_form_class = BlogPostForm
    published_date = models.DateField("Published date")
    updated_date = models.DateField("Updated date", blank=True, null=True)
    summary = models.TextField(blank=True)
    featured_image = models.ForeignKey(
        settings.WAGTAILIMAGES_IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    reading_time = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Estimated reading time in minutes.",
    )
    auto_reading_time = models.BooleanField(
        default=True,
        help_text="Calculate reading time automatically.",
    )
    featured = models.BooleanField(
        default=False,
        help_text="Featured Post on Blog Page."
    )
    show_toc = models.BooleanField(
        default=True,
        help_text="Show table of contents on the post page.",
    )
    
    body = StreamField(
        [
            (
                "heading",
                blocks.RichTextBlock(
                    features=["h2", "h3", "h4", "h5","bold", "italic"],
                ),
            ),
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
        ],
        blank=True,
        use_json_field=True,
    )
    category = models.ForeignKey(
        BlogCategory,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name="blog_posts",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name="blog_posts",
    )
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)

    content_panels = Page.content_panels + [
        "summary",
        
        FieldRowPanel(
            [
                FieldPanel("published_date", classname="col6"),
                FieldPanel("updated_date",  classname="col6"),
                
            ],
            heading="Date",
        ),
        "featured_image",

        "body",
        
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("featured", classname="col6"),
                        FieldPanel("show_toc", classname="col6"),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel(
                            "reading_time",
                            classname="col6 reading-time-field",
                            # Styling lives in blog/static/css/blog-admin.css (see .reading-time-field + .w-field__textoutput).
                            read_only=True,
                        ),
                        FieldPanel("auto_reading_time", classname="col6"),
                    ]
                ),
            ],
            heading="Extras",
        ),
        

        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel(
                            "author",
                            classname="col3",
                            widget=forms.RadioSelect,
                        ),
                        FieldPanel(
                            "category",
                            classname="col6",
                            # Admin grid layout is tied to this class in blog/static/css/blog-admin.css.
                            widget=forms.RadioSelect(attrs={"class": "radio-grid"}),
                        ),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("tags", classname="col6"),
                    ]
                ),
            ],
            heading="Taxonomy",
        ),
    ]
    promote_panels = Page.promote_panels
    parent_page_types = ["blog.BlogPage"]
    subpage_types = []
    template = "blog/blog_post.html"

    def save(self, *args, **kwargs):
        if self.auto_reading_time:
            word_count = self._count_words()
            self.reading_time = (
                max(1, math.ceil(word_count / 200)) if word_count else None
            )
        super().save(*args, **kwargs)
        assign_page_images(self)

    def _count_words(self):
        word_count = 0

        def count_text(text):
            return len(re.findall(r"\b\w+\b", strip_tags(text or "")))

        word_count += count_text(self.summary)
        for block in self.body:
            if block.block_type not in {"heading", "paragraph"}:
                continue
            value = block.value
            if hasattr(value, "source"):
                html = value.source
            else:
                html = str(value)
            word_count += count_text(html)

        return word_count

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        toc_items, toc_map, rendered_map = build_stream_toc(self.body)
        context["blog_toc_items"] = toc_items
        context["blog_toc_map"] = toc_map
        context["blog_toc_rendered"] = rendered_map
        context["show_toc"] = bool(self.show_toc)
        return context


HEADING_RE = re.compile(r"<h([23])([^>]*)>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
HEADING_ID_RE = re.compile(r'\s+id="[^"]*"')


def build_stream_toc(stream_value):
    items = []
    map_items = {}
    rendered_map = {}
    used = {}

    for block in stream_value:
        if block.block_type not in {"heading", "paragraph"}:
            continue
        value = block.value
        html = getattr(value, "source", None) or str(value)
        block_items = []

        def add_heading(level, attrs, inner_html):
            inner_html = re.sub(
                r"</?h[23][^>]*>", "", inner_html, flags=re.IGNORECASE
            )
            text = strip_tags(inner_html).strip()
            if not text:
                return None
            base = slugify(text) or f"section-{len(items) + 1}"
            count = used.get(base, 0) + 1
            used[base] = count
            anchor = base if count == 1 else f"{base}-{count}"
            attrs = HEADING_ID_RE.sub("", (attrs or "")).strip()
            if attrs:
                attrs = f" {attrs}"
            rendered_html = (
                f"<h{level}{attrs} id=\"{anchor}\">{inner_html}</h{level}>"
            )
            item = {
                "id": block.id,
                "level": level,
                "anchor": anchor,
                "text": text,
                "html": inner_html,
                "rendered_html": rendered_html,
            }
            items.append(item)
            block_items.append(item)
            return rendered_html

        def replace(match):
            level = int(match.group(1))
            attrs = match.group(2) or ""
            inner_html = match.group(3)
            rendered_html = add_heading(level, attrs, inner_html)
            return rendered_html or match.group(0)

        new_html = HEADING_RE.sub(replace, html)

        if block.block_type == "heading" and not block_items:
            rendered_html = add_heading(2, "", html)
            if rendered_html:
                new_html = rendered_html

        if block_items:
            rendered_map[block.id] = new_html
            if block.block_type == "heading":
                map_items[block.id] = block_items[0]

    return items, map_items, rendered_map
