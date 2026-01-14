# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='image_height',
            field=models.PositiveIntegerField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='image_width',
            field=models.PositiveIntegerField(blank=True, editable=False, null=True),
        ),
    ]
