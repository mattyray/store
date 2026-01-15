import stripe
from decimal import Decimal

from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.throttling import AnonRateThrottle

from apps.orders.emails import send_contact_form_notification
from .models import Subscriber, GiftCard
from .emails import send_gift_card_email
from .mailerlite import add_subscriber_to_mailerlite


class NewsletterThrottle(AnonRateThrottle):
    scope = 'newsletter'


class ContactThrottle(AnonRateThrottle):
    scope = 'contact'

stripe.api_key = settings.STRIPE_SECRET_KEY


class ContactFormView(APIView):
    """Handle contact form submissions."""
    authentication_classes = []
    permission_classes = []
    throttle_classes = [ContactThrottle]

    def post(self, request):
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip()
        subject = request.data.get('subject', '').strip()
        message = request.data.get('message', '').strip()

        if not all([name, email, message]):
            return Response(
                {'error': 'Name, email, and message are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not subject:
            subject = 'General Inquiry'

        try:
            send_contact_form_notification(name, email, subject, message)
            return Response({'success': True, 'message': 'Message sent successfully'})
        except Exception:
            return Response(
                {'error': 'Failed to send message. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckView(APIView):
    """Simple health check endpoint."""

    def get(self, request):
        return Response({'status': 'ok'})


class NewsletterSubscribeView(APIView):
    """Subscribe to newsletter."""
    authentication_classes = []
    permission_classes = []
    throttle_classes = [NewsletterThrottle]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        name = request.data.get('name', '').strip()
        source = request.data.get('source', 'footer')
        interests = request.data.get('interests', [])

        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            subscriber, created = Subscriber.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'source': source,
                    'interests': interests,
                }
            )

            if not created:
                # Reactivate if previously unsubscribed
                if not subscriber.is_active:
                    subscriber.is_active = True
                    subscriber.unsubscribed_at = None
                    subscriber.save()

            # Sync to MailerLite
            try:
                add_subscriber_to_mailerlite(subscriber)
            except Exception:
                pass  # Don't fail if MailerLite is down

            return Response({
                'success': True,
                'message': 'Thanks for subscribing!',
                'is_new': created
            })

        except IntegrityError:
            return Response({
                'success': True,
                'message': 'You are already subscribed!',
                'is_new': False
            })


class NewsletterUnsubscribeView(APIView):
    """Unsubscribe from newsletter."""

    def post(self, request):
        email = request.data.get('email', '').strip().lower()

        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            subscriber = Subscriber.objects.get(email=email)
            subscriber.unsubscribe()
            return Response({'success': True, 'message': 'You have been unsubscribed.'})
        except Subscriber.DoesNotExist:
            return Response({'success': True, 'message': 'You have been unsubscribed.'})


class GiftCardPurchaseView(APIView):
    """Purchase a gift card."""

    ALLOWED_AMOUNTS = [100, 250, 500, 1000, 2500]

    def post(self, request):
        amount = request.data.get('amount')
        recipient_email = request.data.get('recipient_email', '').strip().lower()
        recipient_name = request.data.get('recipient_name', '').strip()
        purchaser_email = request.data.get('purchaser_email', '').strip().lower()
        purchaser_name = request.data.get('purchaser_name', '').strip()
        message = request.data.get('message', '').strip()

        # Validate amount
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if amount not in self.ALLOWED_AMOUNTS:
            return Response(
                {'error': f'Amount must be one of: {self.ALLOWED_AMOUNTS}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not recipient_email or not purchaser_email:
            return Response(
                {'error': 'Recipient and purchaser email are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create Stripe checkout session for gift card
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': amount * 100,
                        'product_data': {
                            'name': f'${amount} Gift Card',
                            'description': f'Gift card for Matthew Raynor Photography',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{settings.FRONTEND_URL}/gift-card/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/gift-card",
                metadata={
                    'type': 'gift_card',
                    'amount': str(amount),
                    'recipient_email': recipient_email,
                    'recipient_name': recipient_name,
                    'purchaser_email': purchaser_email,
                    'purchaser_name': purchaser_name,
                    'message': message[:500],  # Limit message length
                },
            )

            return Response({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id,
            })

        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class GiftCardCheckView(APIView):
    """Check gift card balance."""

    def post(self, request):
        code = request.data.get('code', '').strip().upper()

        if not code:
            return Response(
                {'error': 'Gift card code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            gift_card = GiftCard.objects.get(code=code)

            if not gift_card.is_valid:
                return Response({
                    'valid': False,
                    'error': 'This gift card is no longer valid',
                })

            return Response({
                'valid': True,
                'balance': str(gift_card.remaining_balance),
                'expires_at': gift_card.expires_at.isoformat() if gift_card.expires_at else None,
            })

        except GiftCard.DoesNotExist:
            return Response(
                {'error': 'Gift card not found'},
                status=status.HTTP_404_NOT_FOUND
            )
