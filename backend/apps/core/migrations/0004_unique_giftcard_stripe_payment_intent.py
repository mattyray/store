from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_increase_giftcard_code_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='giftcard',
            name='stripe_payment_intent',
            field=models.CharField(blank=True, max_length=200, unique=True),
        ),
    ]
