import resend
from django.conf import settings
from django.template.loader import render_to_string

# Initialize Resend with API key
resend.api_key = settings.RESEND_API_KEY


def send_order_confirmation(order):
    """Send order confirmation email to customer."""
    subject = f"Order Confirmed - {order.order_number}"

    # Build items with image URLs
    items_with_images = []
    for item in order.items.select_related('variant__photo', 'product'):
        item_data = {
            'item_title': item.item_title,
            'item_description': item.item_description,
            'quantity': item.quantity,
            'total_price': item.total_price,
            'image_url': None,
        }
        if item.variant and item.variant.photo and item.variant.photo.image:
            item_data['image_url'] = item.variant.photo.image.url
        elif item.product and item.product.image:
            item_data['image_url'] = item.product.image.url
        items_with_images.append(item_data)

    context = {
        'order': order,
        'items': items_with_images,
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

    # Send admin notification
    send_new_order_admin_notification(order, items_with_images)


def send_new_order_admin_notification(order, items):
    """Send notification to admin when new order is placed."""
    subject = f"New Order: {order.order_number} - ${order.total}"

    # Build simple text email for admin
    items_text = "\n".join([
        f"  - {item['item_title']} ({item['item_description']}) x{item['quantity']} = ${item['total_price']}"
        for item in items
    ])

    addr = order.shipping_address
    address_text = f"{addr.get('line1', '')}"
    if addr.get('line2'):
        address_text += f"\n  {addr.get('line2')}"
    address_text += f"\n  {addr.get('city', '')}, {addr.get('state', '')} {addr.get('postal_code', '')}"

    text_body = f"""New order received!

Order: {order.order_number}
Total: ${order.total}

Customer: {order.customer_name}
Email: {order.customer_email}

Items:
{items_text}

Ship to:
  {order.customer_name}
  {address_text}

View in admin: https://store-production-385d.up.railway.app/admin/orders/order/{order.id}/change/
"""

    resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [settings.ADMIN_EMAIL],
        "subject": subject,
        "text": text_body,
    })


def send_shipping_notification(order, tracking_number=None, carrier=None):
    """Send shipping notification email to customer."""
    subject = f"Your Order Has Shipped - {order.order_number}"

    # Build items with image URLs
    items_with_images = []
    for item in order.items.select_related('variant__photo', 'product'):
        item_data = {
            'item_title': item.item_title,
            'item_description': item.item_description,
            'quantity': item.quantity,
            'total_price': item.total_price,
            'image_url': None,
        }
        if item.variant and item.variant.photo and item.variant.photo.image:
            item_data['image_url'] = item.variant.photo.image.url
        elif item.product and item.product.image:
            item_data['image_url'] = item.product.image.url
        items_with_images.append(item_data)

    context = {
        'order': order,
        'items': items_with_images,
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
