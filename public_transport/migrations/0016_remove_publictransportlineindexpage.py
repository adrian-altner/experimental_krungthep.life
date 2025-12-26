from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("public_transport", "0015_publictransportlineindexpage"),
    ]

    operations = [
        migrations.DeleteModel(
            name="PublicTransportLineIndexPage",
        ),
    ]
