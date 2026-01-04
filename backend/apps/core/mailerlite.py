"""MailerLite API integration for newsletter management."""
import requests
from django.conf import settings


MAILERLITE_API_URL = 'https://connect.mailerlite.com/api'


def get_headers():
    return {
        'Authorization': f'Bearer {settings.MAILERLITE_API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }


def add_subscriber_to_mailerlite(subscriber):
    """Add or update a subscriber in MailerLite."""
    if not settings.MAILERLITE_API_KEY:
        return None

    data = {
        'email': subscriber.email,
        'fields': {
            'name': subscriber.name or '',
        },
        'groups': [],  # Add group IDs here if you have specific groups
        'status': 'active' if subscriber.is_active else 'unsubscribed',
    }

    # Add interests as custom field if present
    if subscriber.interests:
        data['fields']['interests'] = ', '.join(subscriber.interests)

    response = requests.post(
        f'{MAILERLITE_API_URL}/subscribers',
        headers=get_headers(),
        json=data,
        timeout=10,
    )

    if response.status_code in [200, 201]:
        result = response.json()
        subscriber.mailerlite_id = result.get('data', {}).get('id', '')
        subscriber.save(update_fields=['mailerlite_id'])
        return result

    return None


def remove_subscriber_from_mailerlite(email):
    """Unsubscribe someone from MailerLite."""
    if not settings.MAILERLITE_API_KEY:
        return None

    # First get the subscriber ID
    response = requests.get(
        f'{MAILERLITE_API_URL}/subscribers/{email}',
        headers=get_headers(),
        timeout=10,
    )

    if response.status_code != 200:
        return None

    subscriber_id = response.json().get('data', {}).get('id')
    if not subscriber_id:
        return None

    # Delete/unsubscribe
    response = requests.delete(
        f'{MAILERLITE_API_URL}/subscribers/{subscriber_id}',
        headers=get_headers(),
        timeout=10,
    )

    return response.status_code == 204
