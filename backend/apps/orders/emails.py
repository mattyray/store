import resend
from django.conf import settings
from django.template.loader import render_to_string

# Initialize Resend with API key
resend.api_key = settings.RESEND_API_KEY


def send_order_confirmation(order):
    """Send order confirmation email to customer."""
    subject = f"Order Confirmed - {order.order_number}"

    context = {
        'order': order,
        'items': order.items.all(),
        'store_name': 'Matthew Raynor Photography',
        'support_email': 'hello@matthewraynor.com',
    }

    html_message = render_to_string('emails/order_confirmation.html', context)
    plain_message = render_to_string('emails/order_confirmation.txt', context)

    resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [order.customer_email],
        "subject": subject,
        "html": html_message,
        "text": plain_message,
    })


def send_shipping_notification(order, tracking_number=None, carrier=None):
    """Send shipping notification email to customer."""
    subject = f"Your Order Has Shipped - {order.order_number}"

    context = {
        'order': order,
        'items': order.items.all(),
        'tracking_number': tracking_number,
        'carrier': carrier,
        'store_name': 'Matthew Raynor Photography',
        'support_email': 'hello@matthewraynor.com',
    }

    html_message = render_to_string('emails/shipping_notification.html', context)
    plain_message = render_to_string('emails/shipping_notification.txt', context)

    resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [order.customer_email],
        "subject": subject,
        "html": html_message,
        "text": plain_message,
    })


def send_contact_form_notification(name, email, subject, message):
    """Send contact form submission to admin."""
    admin_subject = f"Contact Form: {subject}"

    context = {
        'name': name,
        'email': email,
        'subject': subject,
        'message': message,
    }

    html_message = render_to_string('emails/contact_form.html', context)
    plain_message = render_to_string('emails/contact_form.txt', context)

    resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [settings.ADMIN_EMAIL],
        "subject": admin_subject,
        "html": html_message,
        "text": plain_message,
    })

    # Auto-reply to sender
    resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [email],
        "subject": "Thank you for contacting Matthew Raynor Photography",
        "text": f"Hi {name},\n\nThank you for reaching out. I've received your message and will get back to you within 24-48 hours.\n\nBest,\nMatt",
    })
