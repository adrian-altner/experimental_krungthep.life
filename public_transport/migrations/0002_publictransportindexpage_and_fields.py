import django.core.validators
import django.db.models.deletion
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("public_transport", "0001_initial"),
        ("wagtailcore", "0096_referenceindex_referenceindex_source_object_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="PublicTransportIndexPage",
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
        migrations.AddField(
            model_name="publictransportpage",
            name="category",
            field=models.CharField(default="BTS", max_length=50),
        ),
        migrations.AddField(
            model_name="publictransportpage",
            name="system",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="publictransportpage",
            name="line",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="publictransportpage",
            name="station_code",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="publictransportpage",
            name="latitude",
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                max_digits=9,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(-90),
                    django.core.validators.MaxValueValidator(90),
                ],
            ),
        ),
        migrations.AddField(
            model_name="publictransportpage",
            name="longitude",
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                max_digits=9,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(-180),
                    django.core.validators.MaxValueValidator(180),
                ],
            ),
        ),
        migrations.AddField(
            model_name="publictransportpage",
            name="wikidata_id",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name="publictransportpage",
            name="wikidata_url",
            field=models.URLField(blank=True),
        ),
    ]
