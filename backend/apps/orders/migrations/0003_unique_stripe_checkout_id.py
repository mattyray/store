from django.db import migrations, models


def deduplicate_checkout_ids(apps, schema_editor):
    """
    For any duplicate stripe_checkout_id values, keep the most recent order
    and set the older duplicates to NULL. Also convert empty strings to NULL.
    """
    Order = apps.get_model('orders', 'Order')

    # Convert empty strings to NULL
    Order.objects.filter(stripe_checkout_id='').update(stripe_checkout_id=None)

    # Find and fix duplicates: keep the newest, NULL-out the rest
    from django.db.models import Count, Max
    dupes = (
        Order.objects
        .exclude(stripe_checkout_id__isnull=True)
        .values('stripe_checkout_id')
        .annotate(cnt=Count('id'), newest=Max('created_at'))
        .filter(cnt__gt=1)
    )
    for dupe in dupes:
        checkout_id = dupe['stripe_checkout_id']
        # Keep the newest order, NULL-out the rest
        newest_order = (
            Order.objects
            .filter(stripe_checkout_id=checkout_id)
            .order_by('-created_at')
            .first()
        )
        if newest_order:
            Order.objects.filter(
                stripe_checkout_id=checkout_id
            ).exclude(
                pk=newest_order.pk
            ).update(stripe_checkout_id=None)


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_cartitem_unique_together_and_more'),
    ]

    operations = [
        # Step 1: Make field nullable (no unique yet)
        migrations.AlterField(
            model_name='order',
            name='stripe_checkout_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        # Step 2: Deduplicate existing data
        migrations.RunPython(deduplicate_checkout_ids, migrations.RunPython.noop),
        # Step 3: Add unique constraint
        migrations.AlterField(
            model_name='order',
            name='stripe_checkout_id',
            field=models.CharField(blank=True, max_length=200, null=True, unique=True),
        ),
    ]
