from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("public_transport", "0013_merge_20251226_0301"),
    ]

    operations = [
        migrations.DeleteModel(
            name="PublicTransportPage",
        ),
        migrations.DeleteModel(
            name="PublicTransportCategoryPage",
        ),
    ]
