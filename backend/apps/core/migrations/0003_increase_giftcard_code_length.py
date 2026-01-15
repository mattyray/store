from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_create_superuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='giftcard',
            name='code',
            field=models.CharField(editable=False, max_length=19, unique=True),
        ),
    ]
