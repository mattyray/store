from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


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

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.customer_email],
        html_message=html_message,
        fail_silently=False,
    )


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

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.customer_email],
        html_message=html_message,
        fail_silently=False,
    )


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

    send_mail(
        subject=admin_subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        html_message=html_message,
        fail_silently=False,
    )

    # Auto-reply to sender
    send_mail(
        subject="Thank you for contacting Matthew Raynor Photography",
        message=f"Hi {name},\n\nThank you for reaching out. I've received your message and will get back to you within 24-48 hours.\n\nBest,\nMatt",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )
