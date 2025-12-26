from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("public_transport", "0007_system_line_pages_and_filters"),
    ]

    operations = [
        migrations.AddField(
            model_name="publictransportsystempage",
            name="show_stations",
            field=models.BooleanField(
                default=False,
                help_text="Show stations directly on this system page instead of lines.",
            ),
        ),
    ]
