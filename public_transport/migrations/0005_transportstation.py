import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("public_transport", "0004_alter_publictransportpage_line"),
    ]

    operations = [
        migrations.CreateModel(
            name="TransportStation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("station_label", models.CharField(max_length=200)),
                ("station_qid", models.CharField(blank=True, max_length=40)),
                ("system_label", models.CharField(blank=True, max_length=200)),
                ("system_qid", models.CharField(blank=True, max_length=40)),
                ("line_label", models.CharField(blank=True, max_length=200)),
                ("line_qid", models.CharField(blank=True, max_length=40)),
                ("opening", models.DateField(blank=True, null=True)),
                ("station_codes", models.CharField(blank=True, max_length=120)),
                (
                    "latitude",
                    models.DecimalField(
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
                (
                    "longitude",
                    models.DecimalField(
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
                ("raw_properties", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "ordering": ["station_label", "line_label"],
            },
        ),
        migrations.AddConstraint(
            model_name="transportstation",
            constraint=models.UniqueConstraint(
                fields=("station_qid", "line_qid"),
                name="unique_station_per_line",
            ),
        ),
    ]
