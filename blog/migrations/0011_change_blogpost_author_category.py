from django.conf import settings
from django.db import migrations, models


def copy_blogpost_author_category(apps, schema_editor):
    BlogPost = apps.get_model("blog", "BlogPost")
    db_alias = schema_editor.connection.alias

    for post in BlogPost.objects.using(db_alias).all():
        update_fields = []
        if not post.author_id:
            author = post.authors.first()
            if author:
                post.author = author
                update_fields.append("author")
        if not post.category_id:
            category = post.categories.first()
            if category:
                post.category = category
                update_fields.append("category")
        if update_fields:
            post.save(update_fields=update_fields)


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0010_rename_blogpost_dates"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="blogpost",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="+",
                to="blog.blogcategory",
            ),
        ),
        migrations.RunPython(copy_blogpost_author_category, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="blogpost",
            name="authors",
        ),
        migrations.RemoveField(
            model_name="blogpost",
            name="categories",
        ),
        migrations.AlterField(
            model_name="blogpost",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="blog_posts",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="blogpost",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="blog_posts",
                to="blog.blogcategory",
            ),
        ),
    ]
