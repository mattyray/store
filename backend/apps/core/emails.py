import resend
from django.conf import settings
from django.template.loader import render_to_string

# Initialize Resend with API key
resend.api_key = settings.RESEND_API_KEY


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

    resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [gift_card.recipient_email],
        "subject": subject,
        "html": html_message,
        "text": plain_message,
    })


def send_gift_card_purchase_confirmation(gift_card):
    """Send confirmation to purchaser that gift card was sent."""
    subject = f"Gift card sent to {gift_card.recipient_name or gift_card.recipient_email}"

    context = {
        'gift_card': gift_card,
        'store_name': 'Matthew Raynor Photography',
    }

    html_message = render_to_string('emails/gift_card_confirmation.html', context)
    plain_message = render_to_string('emails/gift_card_confirmation.txt', context)

    resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [gift_card.purchaser_email],
        "subject": subject,
        "html": html_message,
        "text": plain_message,
    })
