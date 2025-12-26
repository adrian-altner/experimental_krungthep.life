from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("public_transport", "0008_systempage_show_stations"),
    ]

    operations = [
        migrations.AddField(
            model_name="publictransportsystempage",
            name="station_sort",
            field=models.CharField(
                choices=[
                    ("station_label", "Station name (A-Z)"),
                    ("-station_label", "Station name (Z-A)"),
                    ("opening", "Opening date (oldest first)"),
                    ("-opening", "Opening date (newest first)"),
                    ("line_label", "Line (A-Z)"),
                    ("station_codes", "Station code (A-Z)"),
                ],
                default="station_label",
                max_length=40,
            ),
        ),
    ]
