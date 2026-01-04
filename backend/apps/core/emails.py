from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_gift_card_email(gift_card):
    """Send gift card to recipient."""
    subject = f"You've received a gift card from {gift_card.purchaser_name or 'a friend'}!"

    context = {
        'gift_card': gift_card,
        'store_name': 'Matthew Raynor Photography',
        'store_url': settings.FRONTEND_URL,
    }

    html_message = render_to_string('emails/gift_card.html', context)
    plain_message = render_to_string('emails/gift_card.txt', context)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[gift_card.recipient_email],
        html_message=html_message,
        fail_silently=False,
    )


def send_gift_card_purchase_confirmation(gift_card):
    """Send confirmation to purchaser that gift card was sent."""
    subject = f"Gift card sent to {gift_card.recipient_name or gift_card.recipient_email}"

    context = {
        'gift_card': gift_card,
        'store_name': 'Matthew Raynor Photography',
    }

    html_message = render_to_string('emails/gift_card_confirmation.html', context)
    plain_message = render_to_string('emails/gift_card_confirmation.txt', context)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[gift_card.purchaser_email],
        html_message=html_message,
        fail_silently=False,
    )
