from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_cartitem_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='stripe_checkout_id',
            field=models.CharField(blank=True, max_length=200, unique=True),
        ),
    ]
