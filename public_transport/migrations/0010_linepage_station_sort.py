from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("public_transport", "0009_systempage_station_sort"),
    ]

    operations = [
        migrations.AddField(
            model_name="publictransportlinepage",
            name="station_sort",
            field=models.CharField(
                choices=[
                    ("station_label", "Station name (A-Z)"),
                    ("-station_label", "Station name (Z-A)"),
                    ("opening", "Opening date (oldest first)"),
                    ("-opening", "Opening date (newest first)"),
                    ("station_codes", "Station code (A-Z)"),
                ],
                default="station_label",
                max_length=40,
            ),
        ),
    ]
