from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0009_remove_blogpost_intro"),
    ]

    operations = [
        migrations.RenameField(
            model_name="blogpost",
            old_name="date",
            new_name="published_date",
        ),
        migrations.RenameField(
            model_name="blogpost",
            old_name="publish_date",
            new_name="updated_date",
        ),
    ]
