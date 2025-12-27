from django.conf import settings
from django.db import migrations, models


def fill_missing_author_category(apps, schema_editor):
    BlogPost = apps.get_model("blog", "BlogPost")
    BlogCategory = apps.get_model("blog", "BlogCategory")
    user_app_label, user_model_name = settings.AUTH_USER_MODEL.split(".")
    UserModel = apps.get_model(user_app_label, user_model_name)
    db_alias = schema_editor.connection.alias

    default_author = UserModel.objects.using(db_alias).order_by("pk").first()
    default_category = BlogCategory.objects.using(db_alias).order_by("pk").first()

    missing_authors = BlogPost.objects.using(db_alias).filter(author__isnull=True)
    if missing_authors.exists():
        if not default_author:
            raise RuntimeError("Cannot set required author: no users exist.")
        missing_authors.update(author=default_author)

    missing_categories = BlogPost.objects.using(db_alias).filter(category__isnull=True)
    if missing_categories.exists():
        if not default_category:
            raise RuntimeError("Cannot set required category: no categories exist.")
        missing_categories.update(category=default_category)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("blog", "0011_change_blogpost_author_category"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(fill_missing_author_category, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="blogpost",
            name="author",
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name="blog_posts",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="blogpost",
            name="category",
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name="blog_posts",
                to="blog.blogcategory",
            ),
        ),
    ]
