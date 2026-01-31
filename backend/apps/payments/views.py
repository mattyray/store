import json
import logging
import stripe
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from apps.catalog.models import ProductVariant, Product
from apps.orders.models import Cart, Order, OrderItem
from apps.orders.views import get_or_create_cart
from apps.orders.emails import send_order_confirmation
from apps.core.models import GiftCard, GiftCardRedemption, Subscriber
from apps.core.emails import send_gift_card_email, send_gift_card_purchase_confirmation

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    """Create a Stripe Checkout session for the current cart."""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        cart = get_or_create_cart(request)

        if not cart.items.exists():
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for gift card code
        gift_card_code = request.data.get('gift_card_code', '').strip().upper()
        gift_card = None
        gift_card_amount = 0

        if gift_card_code:
            try:
                gift_card = GiftCard.objects.get(code=gift_card_code)
                if not gift_card.is_valid:
                    return Response(
                        {'error': 'Gift card is no longer valid'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Calculate how much of the gift card to use
                cart_total = cart.subtotal
                gift_card_amount = min(gift_card.remaining_balance, cart_total)
            except GiftCard.DoesNotExist:
                return Response(
                    {'error': 'Gift card not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        line_items = []
        cart_snapshot = []
        for item in cart.items.select_related('variant__photo', 'product'):
            if item.variant:
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
                cart_snapshot.append({
                    't': 'v', 'id': item.variant.id,
                    'q': item.quantity, 'p': str(item.variant.price),
                })
            elif item.product:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(item.product.price * 100),
                        'product_data': {
                            'name': item.product.title,
                            'description': item.product.get_product_type_display(),
                            'images': [
                                request.build_absolute_uri(item.product.image.url)
                            ] if item.product.image else [],
                        },
                    },
                    'quantity': item.quantity,
                })
                cart_snapshot.append({
                    't': 'p', 'id': item.product.id,
                    'q': item.quantity, 'p': str(item.product.price),
                })

        try:
            # Build checkout session params
            checkout_params = {
                'payment_method_types': ['card'],
                'line_items': line_items,
                'mode': 'payment',
                'success_url': f"{settings.FRONTEND_URL}/order/success?session_id={{CHECKOUT_SESSION_ID}}",
                'cancel_url': f"{settings.FRONTEND_URL}/cart",
                'shipping_address_collection': {
                    'allowed_countries': ['US'],
                },
                'billing_address_collection': 'required',
                'metadata': {
                    'cart_id': str(cart.id),
                    'cart_snapshot': json.dumps(cart_snapshot),
                },
            }

            # Apply gift card as a Stripe coupon/discount
            if gift_card and gift_card_amount > 0:
                # Create a one-time coupon for the gift card amount
                coupon = stripe.Coupon.create(
                    amount_off=int(gift_card_amount * 100),
                    currency='usd',
                    duration='once',
                    name=f'Gift Card {gift_card.code}',
                )
                checkout_params['discounts'] = [{'coupon': coupon.id}]
                checkout_params['metadata']['gift_card_code'] = gift_card.code
                checkout_params['metadata']['gift_card_amount'] = str(gift_card_amount)
            else:
                # Only allow promo codes when no gift card is applied
                # (Stripe doesn't allow both discounts and allow_promotion_codes)
                checkout_params['allow_promotion_codes'] = True

            checkout_session = stripe.checkout.Session.create(**checkout_params)

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
            metadata = session.get('metadata', {})

            # Check if this is a gift card purchase
            if metadata.get('type') == 'gift_card':
                self.handle_gift_card_purchase(session)
            else:
                self.handle_checkout_completed(session)

        return HttpResponse(status=200)

    def handle_checkout_completed(self, session):
        """Create order from completed checkout session."""
        # Idempotency: skip if we already processed this session
        if Order.objects.filter(stripe_checkout_id=session['id']).exists():
            logger.info(f"Order already exists for session {session['id']}, skipping")
            return

        metadata = session.get('metadata', {})
        cart_id = metadata.get('cart_id')
        if not cart_id:
            return

        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            return

        shipping = session.get('shipping_details', {})
        address = shipping.get('address', {})

        # Wrap order creation, items, gift card redemption, and cart
        # cleanup in a single transaction for data consistency
        with transaction.atomic():
            order = Order.objects.create(
                stripe_checkout_id=session['id'],
                stripe_payment_intent=session.get('payment_intent') or '',
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

            # Use cart snapshot from metadata to ensure prices match what
            # was charged. Fall back to live cart for older sessions.
            snapshot_raw = metadata.get('cart_snapshot')
            snapshot_items = json.loads(snapshot_raw) if snapshot_raw else None

            if snapshot_items:
                self._create_order_items_from_snapshot(order, snapshot_items)
            else:
                self._create_order_items_from_cart(order, cart)

            # Redeem gift card with row locking to prevent double-spend
            gift_card_code = metadata.get('gift_card_code')
            gift_card_amount = metadata.get('gift_card_amount')
            if gift_card_code and gift_card_amount:
                try:
                    # select_for_update locks the row until transaction commits
                    gift_card = GiftCard.objects.select_for_update().get(
                        code=gift_card_code
                    )
                    amount = Decimal(gift_card_amount)
                    redeemed = gift_card.redeem(amount)
                    if redeemed > 0:
                        GiftCardRedemption.objects.create(
                            gift_card=gift_card,
                            order=order,
                            amount=redeemed,
                        )
                except GiftCard.DoesNotExist:
                    logger.warning(f"Gift card {gift_card_code} not found during redemption")
                except Exception:
                    logger.exception("Gift card redemption failed")

            cart.items.all().delete()

        # Send confirmation email (outside transaction — don't rollback
        # the order if email fails)
        try:
            send_order_confirmation(order)
        except Exception:
            logger.exception(f"Failed to send confirmation email for order {order.order_number}")

        # Add customer to newsletter subscriber list
        if order.customer_email:
            try:
                Subscriber.objects.get_or_create(
                    email=order.customer_email.lower(),
                    defaults={
                        'name': order.customer_name,
                        'source': 'purchase',
                    }
                )
            except Exception:
                pass

    def _create_order_items_from_snapshot(self, order, snapshot_items):
        """Create order items using the price snapshot from checkout time."""
        for snap in snapshot_items:
            quantity = snap['q']
            price = Decimal(snap['p'])
            total = price * quantity

            if snap['t'] == 'v':
                try:
                    variant = ProductVariant.objects.select_related('photo').get(
                        id=snap['id']
                    )
                    OrderItem.objects.create(
                        order=order,
                        variant=variant,
                        item_title=variant.photo.title,
                        item_description=variant.display_name,
                        quantity=quantity,
                        unit_price=price,
                        total_price=total,
                    )
                except ProductVariant.DoesNotExist:
                    logger.error(f"Variant {snap['id']} not found for order {order.order_number}")
            elif snap['t'] == 'p':
                try:
                    product = Product.objects.get(id=snap['id'])
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        item_title=product.title,
                        item_description=product.get_product_type_display(),
                        quantity=quantity,
                        unit_price=price,
                        total_price=total,
                    )
                    # Atomic stock decrement to prevent race conditions
                    if product.track_inventory:
                        updated = Product.objects.filter(
                            id=product.id,
                            stock_quantity__gte=quantity,
                        ).update(stock_quantity=F('stock_quantity') - quantity)
                        if not updated:
                            logger.warning(
                                f"Insufficient stock for product {product.id} "
                                f"(requested {quantity})"
                            )
                except Product.DoesNotExist:
                    logger.error(f"Product {snap['id']} not found for order {order.order_number}")

    def _create_order_items_from_cart(self, order, cart):
        """Fallback: create order items from live cart (for older sessions without snapshot)."""
        for item in cart.items.select_related('variant__photo', 'product'):
            if item.variant:
                OrderItem.objects.create(
                    order=order,
                    variant=item.variant,
                    item_title=item.variant.photo.title,
                    item_description=item.variant.display_name,
                    quantity=item.quantity,
                    unit_price=item.variant.price,
                    total_price=item.total_price,
                )
            elif item.product:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    item_title=item.product.title,
                    item_description=item.product.get_product_type_display(),
                    quantity=item.quantity,
                    unit_price=item.product.price,
                    total_price=item.total_price,
                )
                # Atomic stock decrement to prevent race conditions
                if item.product.track_inventory:
                    updated = Product.objects.filter(
                        id=item.product.id,
                        stock_quantity__gte=item.quantity,
                    ).update(stock_quantity=F('stock_quantity') - item.quantity)
                    if not updated:
                        logger.warning(
                            f"Insufficient stock for product {item.product.id} "
                            f"(requested {item.quantity})"
                        )

    def handle_gift_card_purchase(self, session):
        """Create gift card from completed checkout session."""
        metadata = session.get('metadata', {})

        amount = Decimal(metadata.get('amount', '0'))
        if amount <= 0:
            return

        gift_card = GiftCard.objects.create(
            initial_amount=amount,
            remaining_balance=amount,
            purchaser_email=metadata.get('purchaser_email', ''),
            purchaser_name=metadata.get('purchaser_name', ''),
            recipient_email=metadata.get('recipient_email', ''),
            recipient_name=metadata.get('recipient_name', ''),
            message=metadata.get('message', ''),
            stripe_payment_intent=session.get('payment_intent', ''),
        )

        # Send emails
        try:
            send_gift_card_email(gift_card)
            gift_card.mark_sent()
        except Exception:
            pass

        try:
            send_gift_card_purchase_confirmation(gift_card)
        except Exception:
            pass

        # Add gift card purchaser to subscriber list
        if gift_card.purchaser_email:
            try:
                Subscriber.objects.get_or_create(
                    email=gift_card.purchaser_email.lower(),
                    defaults={
                        'name': gift_card.purchaser_name,
                        'source': 'gift_card_purchase',
                    }
                )
            except Exception:
                pass


class OrderLookupView(APIView):
    """Look up order by Stripe session ID."""
    authentication_classes = []
    permission_classes = []

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
