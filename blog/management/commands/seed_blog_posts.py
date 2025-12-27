from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.text import slugify
from faker import Faker
from wagtail.blocks import StreamValue

from blog.models import BlogPage, BlogPost


class Command(BaseCommand):
    help = "Seed fake blog posts under the first BlogPage."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=10)
        parser.add_argument("--seed", type=int, default=None)
        parser.add_argument("--locale", type=str, default="en_US")

    def handle(self, *args, **options):
        count = options["count"]
        if count < 1:
            raise CommandError("count must be >= 1")

        blog_root = BlogPage.objects.first()
        if not blog_root:
            raise CommandError("No BlogPage found. Create one first.")
        child_count = blog_root.get_children().count()
        if blog_root.numchild != child_count:
            blog_root.numchild = child_count
            blog_root.save(update_fields=["numchild"])

        faker = Faker(options["locale"])
        if options["seed"] is not None:
            faker.seed_instance(options["seed"])

        users = list(get_user_model().objects.all())
        now = timezone.now().date()

        for index in range(count):
            title = faker.sentence(nb_words=6).rstrip(".")
            base_slug = slugify(title) or f"post-{index + 1}"
            slug = self._unique_slug(blog_root, base_slug)

            intro = faker.text(max_nb_chars=180)
            summary = faker.paragraph(nb_sentences=3)
            publish_date = now - timedelta(days=index)

            stream_block = BlogPost._meta.get_field("body").stream_block
            body = StreamValue(
                stream_block,
                [
                    ("heading", faker.sentence(nb_words=5).rstrip(".")),
                    ("paragraph", faker.paragraph(nb_sentences=4)),
                ],
                is_lazy=False,
            )

            post = BlogPost(
                title=title,
                slug=slug,
                date=publish_date,
                intro=intro,
                summary=summary,
                publish_date=publish_date,
                body=body,
            )

            blog_root.add_child(instance=post)
            revision = post.save_revision()
            revision.publish()

            if users:
                post.authors.set(faker.random_elements(users, length=min(2, len(users)), unique=True))

            self.stdout.write(f"Created: {post.title}")

    def _unique_slug(self, parent, base_slug: str) -> str:
        slug = base_slug
        suffix = 2
        while parent.get_children().filter(slug=slug).exists():
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        return slug
