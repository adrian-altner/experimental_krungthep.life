import django.db.models.deletion
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("public_transport", "0014_remove_legacy_pages"),
    ]

    operations = [
        migrations.CreateModel(
            name="PublicTransportLineIndexPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("intro", wagtail.fields.RichTextField(blank=True)),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
    ]
