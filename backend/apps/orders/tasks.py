import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def cleanup_stale_carts(days: int = 30):
    """
    Delete carts older than specified days that have no associated order.

    Args:
        days: Delete carts older than this many days (default 30)

    Returns:
        Number of carts deleted
    """
    from .models import Cart

    cutoff = timezone.now() - timedelta(days=days)
    stale_carts = Cart.objects.filter(
        created_at__lt=cutoff,
        updated_at__lt=cutoff,
    )

    count = stale_carts.count()
    if count > 0:
        stale_carts.delete()
        logger.info(f'Cleaned up {count} stale carts older than {days} days')

    return count
