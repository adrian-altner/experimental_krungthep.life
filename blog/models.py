from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import Tag, TaggedItemBase
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.snippets.models import register_snippet
from django.http import Http404
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
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]
    parent_page_types = ["home.HomePage"]
    subpage_types = ["blog.BlogPost"]
    template = "blog/blog_page.html"

    def get_base_posts(self):
        return BlogPost.objects.child_of(self).live()  # type: ignore[attr-defined]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        all_posts = self.get_base_posts()
        posts = all_posts.order_by("-date")
        tag_slug = request.GET.get("tag")
        category_slug = request.GET.get("category")
        author_slug = request.GET.get("author")
        if tag_slug:
            posts = posts.filter(tags__slug=tag_slug)
        if category_slug:
            posts = posts.filter(categories__slug=category_slug)
        if author_slug:
            posts = posts.filter(authors__author_slug=author_slug)
        context["posts"] = posts
        context["active_tag"] = tag_slug
        context["active_category"] = category_slug
        context["active_author"] = author_slug
        context["categories"] = BlogCategory.objects.all()
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
        posts = self.get_base_posts().filter(authors=author).order_by("-date")
        context = self.get_context(request)
        context["author"] = author
        context["posts"] = posts
        return self.render(
            request,
            context_overrides=context,
            template="blog/author_detail.html",
        )


class BlogPost(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    summary = models.TextField(blank=True)
    reading_time = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Estimated reading time in minutes.",
    )
    featured = models.BooleanField(default=False)
    publish_date = models.DateField(blank=True, null=True)
    featured_image = models.ForeignKey(
        settings.WAGTAILIMAGES_IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title")),
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
        ],
        blank=True,
        use_json_field=True,
    )
    categories = ParentalManyToManyField(BlogCategory, blank=True)
    authors = ParentalManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="blog_posts"
    )
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("date"),
                FieldPanel("publish_date"),
                FieldPanel("featured_image"),
                FieldPanel("intro"),
            ],
            heading="Post",
        ),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("authors"),
                FieldPanel("categories"),
                FieldPanel("tags"),
                FieldPanel("summary"),
                FieldPanel("reading_time"),
                FieldPanel("featured"),
            ],
            heading="Taxonomy",
        ),
    ]
    promote_panels = Page.promote_panels + [
        FieldPanel("seo_title"),
        FieldPanel("search_description"),
    ]
    parent_page_types = ["blog.BlogPage"]
    subpage_types = []
    template = "blog/blog_post.html"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        assign_page_images(self)
