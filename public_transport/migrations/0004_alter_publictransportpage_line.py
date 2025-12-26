from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("public_transport", "0003_publictransportcategorypage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="publictransportpage",
            name="line",
            field=models.TextField(blank=True),
        ),
    ]
