import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Cart, Order, OrderItem
from apps.orders.views import get_or_create_cart

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    """Create a Stripe Checkout session for the current cart."""

    def post(self, request):
        cart = get_or_create_cart(request)

        if not cart.items.exists():
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        line_items = []
        for item in cart.items.select_related('variant__photo'):
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(item.variant.price * 100),
                    'product_data': {
                        'name': item.variant.photo.title,
                        'description': item.variant.display_name,
                        'images': [
                            request.build_absolute_uri(item.variant.photo.image.url)
                        ] if item.variant.photo.image else [],
                    },
                },
                'quantity': item.quantity,
            })

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=f"{settings.FRONTEND_URL}/order/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/cart",
                shipping_address_collection={
                    'allowed_countries': ['US'],
                },
                billing_address_collection='required',
                metadata={
                    'cart_id': str(cart.id),
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


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """Handle Stripe webhook events."""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self.handle_checkout_completed(session)

        return HttpResponse(status=200)

    def handle_checkout_completed(self, session):
        """Create order from completed checkout session."""
        cart_id = session.get('metadata', {}).get('cart_id')
        if not cart_id:
            return

        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            return

        shipping = session.get('shipping_details', {})
        address = shipping.get('address', {})

        order = Order.objects.create(
            stripe_checkout_id=session['id'],
            stripe_payment_intent=session.get('payment_intent', ''),
            customer_email=session.get('customer_details', {}).get('email', ''),
            customer_name=shipping.get('name', ''),
            shipping_address={
                'line1': address.get('line1', ''),
                'line2': address.get('line2', ''),
                'city': address.get('city', ''),
                'state': address.get('state', ''),
                'postal_code': address.get('postal_code', ''),
                'country': address.get('country', ''),
            },
            status='paid',
            subtotal=cart.subtotal,
            total=session.get('amount_total', 0) / 100,
        )

        for item in cart.items.select_related('variant__photo'):
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                photo_title=item.variant.photo.title,
                variant_description=item.variant.display_name,
                quantity=item.quantity,
                unit_price=item.variant.price,
                total_price=item.total_price,
            )

        cart.items.all().delete()


class OrderLookupView(APIView):
    """Look up order by Stripe session ID."""

    def get(self, request):
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response(
                {'error': 'session_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = Order.objects.get(stripe_checkout_id=session_id)
            return Response({
                'order_number': order.order_number,
                'customer_email': order.customer_email,
                'total': str(order.total),
                'status': order.status,
            })
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
