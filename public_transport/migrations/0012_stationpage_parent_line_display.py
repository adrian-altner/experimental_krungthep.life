from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("public_transport", "0011_publictransportstationpage"),
    ]

    operations = [
        migrations.AddField(
            model_name="publictransportstationpage",
            name="parent_line_display",
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
