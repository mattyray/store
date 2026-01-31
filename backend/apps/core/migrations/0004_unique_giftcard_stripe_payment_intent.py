from django.db import migrations, models


def convert_empty_to_null(apps, schema_editor):
    GiftCard = apps.get_model('core', 'GiftCard')
    GiftCard.objects.filter(stripe_payment_intent='').update(stripe_payment_intent=None)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_increase_giftcard_code_length'),
    ]

    operations = [
        # Step 1: Make field nullable (no unique yet) so we can convert '' to NULL
        migrations.AlterField(
            model_name='giftcard',
            name='stripe_payment_intent',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        # Step 2: Convert existing empty strings to NULL
        migrations.RunPython(convert_empty_to_null, migrations.RunPython.noop),
        # Step 3: Now add the unique constraint
        migrations.AlterField(
            model_name='giftcard',
            name='stripe_payment_intent',
            field=models.CharField(blank=True, max_length=200, null=True, unique=True),
        ),
    ]
