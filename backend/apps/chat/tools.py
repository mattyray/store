"""
LangChain tools for the AI shopping agent.

Each tool is a function the agent can call to take actions
like searching photos, managing cart, generating mockups, etc.
"""
from typing import Optional
from decimal import Decimal

from django.conf import settings
from django.db.models import Q

from langchain_core.tools import tool
from openai import OpenAI

from apps.catalog.models import Photo, Collection, ProductVariant
from apps.orders.models import Cart, CartItem
from apps.core.models import GiftCard


def get_openai_client():
    """Get OpenAI client for embeddings."""
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def get_absolute_url(file_field):
    """Convert a file field to an absolute URL for the frontend."""
    if not file_field:
        return None
    url = file_field.url
    # If already absolute, return as-is
    if url.startswith('http'):
        return url
    # Build absolute URL using FRONTEND_URL or localhost
    base_url = getattr(settings, 'BACKEND_URL', 'http://localhost:7974')
    return f"{base_url}{url}"


def generate_query_embedding(query: str) -> list:
    """Generate embedding for a search query."""
    client = get_openai_client()
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=query,
    )
    return response.data[0].embedding


# ============================================================================
# SEARCH & BROWSE TOOLS
# ============================================================================

@tool
def search_photos_semantic(query: str, limit: int = 5) -> list:
    """
    Search for photos by meaning/vibe using semantic similarity.

    Use this when the customer describes what they're looking for in natural language,
    like "something calm and blue for my bedroom" or "dramatic sunset over the ocean".

    Args:
        query: Natural language description of what the customer wants
        limit: Maximum number of results to return (default 5)

    Returns:
        List of matching photos with details
    """
    try:
        # Generate embedding for the query
        query_embedding = generate_query_embedding(query)

        # Use pgvector to find similar photos
        # Note: This requires the embedding field to be populated
        photos = Photo.objects.filter(
            is_active=True,
            embedding__isnull=False
        ).order_by(
            # Cosine distance - lower is more similar
            # pgvector uses <=> operator for cosine distance
        )[:limit * 2]  # Get more, then filter

        # For now, fall back to text-based search if embeddings aren't ready
        if not photos.exists():
            photos = Photo.objects.filter(
                Q(ai_description__icontains=query) |
                Q(title__icontains=query) |
                Q(ai_mood__icontains=query) |
                Q(ai_subjects__icontains=query)
            ).filter(is_active=True)[:limit]

        results = []
        for photo in photos[:limit]:
            price_range = photo.price_range
            results.append({
                'id': photo.id,
                'slug': photo.slug,
                'title': photo.title,
                'description': photo.ai_description or photo.description,
                'colors': photo.ai_colors,
                'mood': photo.ai_mood,
                'subjects': photo.ai_subjects,
                'collection': photo.collection.name if photo.collection else None,
                'price_range': {
                    'min': float(price_range['min']) if price_range else None,
                    'max': float(price_range['max']) if price_range else None,
                } if price_range else None,
                'image_url': get_absolute_url(photo.image),
                'thumbnail_url': get_absolute_url(photo.thumbnail) or get_absolute_url(photo.image),
                'url': f'/photos/{photo.slug}',
            })

        return results

    except Exception as e:
        return {'error': str(e)}


@tool
def search_photos_filter(
    collection: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    material: Optional[str] = None,
    limit: int = 10
) -> list:
    """
    Filter photos by specific criteria like collection, price, or material.

    Use this when the customer has specific requirements like "photos under $1000"
    or "prints from the Montauk collection".

    Args:
        collection: Filter by collection slug (e.g., "aerial-photography", "shots-from-the-sea")
        min_price: Minimum price filter
        max_price: Maximum price filter
        material: Filter by material type ("paper" or "aluminum")
        limit: Maximum results to return

    Returns:
        List of matching photos with details
    """
    try:
        photos = Photo.objects.filter(is_active=True)

        if collection:
            photos = photos.filter(collection__slug__iexact=collection)

        # Price filtering requires joining with variants
        if min_price is not None or max_price is not None or material:
            variant_filters = Q(variants__is_available=True)

            if min_price is not None:
                variant_filters &= Q(variants__price__gte=min_price)
            if max_price is not None:
                variant_filters &= Q(variants__price__lte=max_price)
            if material:
                variant_filters &= Q(variants__material__iexact=material)

            photos = photos.filter(variant_filters).distinct()

        results = []
        for photo in photos[:limit]:
            price_range = photo.price_range
            results.append({
                'id': photo.id,
                'slug': photo.slug,
                'title': photo.title,
                'description': photo.ai_description or photo.description,
                'collection': photo.collection.name if photo.collection else None,
                'price_range': {
                    'min': float(price_range['min']) if price_range else None,
                    'max': float(price_range['max']) if price_range else None,
                } if price_range else None,
                'image_url': get_absolute_url(photo.image),
                'thumbnail_url': get_absolute_url(photo.thumbnail) or get_absolute_url(photo.image),
                'url': f'/photos/{photo.slug}',
            })

        return results

    except Exception as e:
        return {'error': str(e)}


@tool
def get_photo_details(photo_slug: str) -> dict:
    """
    Get full details for a specific photo including all available variants.

    Use this when you need to show a customer complete information about a photo,
    including all size and material options with prices.

    Args:
        photo_slug: The slug identifier for the photo

    Returns:
        Complete photo details with all variants
    """
    try:
        photo = Photo.objects.get(slug=photo_slug, is_active=True)

        variants = []
        for v in photo.variants.filter(is_available=True).order_by('price'):
            variants.append({
                'id': v.id,
                'size': v.size,
                'material': v.material,
                'material_display': v.get_material_display(),
                'price': float(v.price),
                'width_inches': v.width_inches,
                'height_inches': v.height_inches,
            })

        return {
            'id': photo.id,
            'slug': photo.slug,
            'title': photo.title,
            'description': photo.ai_description or photo.description,
            'location': photo.location,
            'colors': photo.ai_colors,
            'mood': photo.ai_mood,
            'subjects': photo.ai_subjects,
            'room_suggestions': photo.ai_room_suggestions,
            'collection': photo.collection.name if photo.collection else None,
            'image_url': photo.image.url if photo.image else None,
            'thumbnail_url': photo.thumbnail.url if photo.thumbnail else (photo.image.url if photo.image else None),
            'url': f'/photos/{photo.slug}',
            'variants': variants,
        }

    except Photo.DoesNotExist:
        return {'error': f'Photo not found: {photo_slug}'}
    except Exception as e:
        return {'error': str(e)}


@tool
def get_collections() -> list:
    """
    List all available photo collections.

    Use this to show customers what collections are available or when they
    ask about different series/themes of photographs.

    Returns:
        List of all active collections with descriptions
    """
    try:
        collections = Collection.objects.filter(is_active=True).order_by('display_order')

        results = []
        for c in collections:
            results.append({
                'slug': c.slug,
                'name': c.name,
                'description': c.description,
                'photo_count': c.photo_count,
            })

        return results

    except Exception as e:
        return {'error': str(e)}


# ============================================================================
# CART TOOLS
# ============================================================================

@tool
def add_to_cart(photo_slug: str, variant_id: int, quantity: int = 1, cart_id: str = None) -> dict:
    """
    Add a print to the customer's shopping cart.

    Use this when a customer wants to add an item to their cart.
    Always confirm with the customer which size/material they want before adding.

    Args:
        photo_slug: The photo slug to add
        variant_id: The specific variant (size/material) ID
        quantity: Number to add (default 1)
        cart_id: Cart ID (will be provided by context)

    Returns:
        Updated cart summary
    """
    try:
        variant = ProductVariant.objects.get(id=variant_id, is_available=True)

        # Get or create cart
        if cart_id:
            cart, _ = Cart.objects.get_or_create(id=cart_id)
        else:
            cart = Cart.objects.create()

        # Check if item already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return {
            'success': True,
            'message': f'Added {variant.photo.title} ({variant.display_name}) to cart',
            'cart_id': str(cart.id),
            'cart_total': float(cart.total),
            'cart_item_count': cart.item_count,
        }

    except ProductVariant.DoesNotExist:
        return {'error': 'Variant not found or not available'}
    except Exception as e:
        return {'error': str(e)}


@tool
def get_cart(cart_id: str = None) -> dict:
    """
    Get the current cart contents.

    Use this to show customers what's in their cart or before checkout.

    Args:
        cart_id: Cart ID (will be provided by context)

    Returns:
        Cart contents with items and totals
    """
    try:
        if not cart_id:
            return {'items': [], 'total': 0, 'item_count': 0}

        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            return {'items': [], 'total': 0, 'item_count': 0}

        items = []
        for item in cart.items.all():
            if item.variant:
                items.append({
                    'id': item.id,
                    'photo_title': item.variant.photo.title,
                    'variant': item.variant.display_name,
                    'price': float(item.variant.price),
                    'quantity': item.quantity,
                    'subtotal': float(item.subtotal),
                })
            elif item.product:
                items.append({
                    'id': item.id,
                    'product_title': item.product.title,
                    'price': float(item.product.price),
                    'quantity': item.quantity,
                    'subtotal': float(item.subtotal),
                })

        return {
            'cart_id': str(cart.id),
            'items': items,
            'total': float(cart.total),
            'item_count': cart.item_count,
            'free_shipping': cart.total >= 500,
        }

    except Exception as e:
        return {'error': str(e)}


@tool
def remove_from_cart(item_id: int, cart_id: str = None) -> dict:
    """
    Remove an item from the cart.

    Args:
        item_id: The cart item ID to remove
        cart_id: Cart ID (will be provided by context)

    Returns:
        Updated cart summary
    """
    try:
        if not cart_id:
            return {'error': 'No cart found'}

        cart = Cart.objects.get(id=cart_id)
        item = CartItem.objects.get(id=item_id, cart=cart)
        item_name = str(item)
        item.delete()

        return {
            'success': True,
            'message': f'Removed {item_name} from cart',
            'cart_total': float(cart.total),
            'cart_item_count': cart.item_count,
        }

    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return {'error': 'Item not found in cart'}
    except Exception as e:
        return {'error': str(e)}


@tool
def update_cart_item(item_id: int, quantity: int, cart_id: str = None) -> dict:
    """
    Update the quantity of a cart item.

    Args:
        item_id: The cart item ID to update
        quantity: New quantity (0 to remove)
        cart_id: Cart ID (will be provided by context)

    Returns:
        Updated cart summary
    """
    try:
        if not cart_id:
            return {'error': 'No cart found'}

        cart = Cart.objects.get(id=cart_id)
        item = CartItem.objects.get(id=item_id, cart=cart)

        if quantity <= 0:
            item.delete()
            message = 'Item removed from cart'
        else:
            item.quantity = quantity
            item.save()
            message = f'Updated quantity to {quantity}'

        return {
            'success': True,
            'message': message,
            'cart_total': float(cart.total),
            'cart_item_count': cart.item_count,
        }

    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return {'error': 'Item not found in cart'}
    except Exception as e:
        return {'error': str(e)}


# ============================================================================
# CHECKOUT TOOLS
# ============================================================================

@tool
def start_checkout(cart_id: str = None) -> dict:
    """
    Start the checkout process and get a Stripe checkout URL.

    Use this when the customer is ready to purchase. Returns a URL
    they can click to complete payment.

    Args:
        cart_id: Cart ID (will be provided by context)

    Returns:
        Checkout URL or error
    """
    try:
        if not cart_id:
            return {'error': 'No cart found'}

        cart = Cart.objects.get(id=cart_id)

        if cart.item_count == 0:
            return {'error': 'Cart is empty'}

        # Return the checkout URL - frontend will handle Stripe session creation
        checkout_url = f"{settings.FRONTEND_URL}/checkout?cart={cart_id}"

        return {
            'success': True,
            'checkout_url': checkout_url,
            'cart_total': float(cart.total),
            'message': 'Ready for checkout! Click the link to complete your purchase.',
        }

    except Cart.DoesNotExist:
        return {'error': 'Cart not found'}
    except Exception as e:
        return {'error': str(e)}


# ============================================================================
# ORDER TOOLS
# ============================================================================

@tool
def track_order(order_number: str = None, email: str = None) -> dict:
    """
    Look up an order status.

    Use this when a customer wants to check on their order.
    They need to provide either an order number or their email.

    Args:
        order_number: The order number (e.g., "ORD-12345")
        email: Customer's email address

    Returns:
        Order status and details
    """
    try:
        from apps.orders.models import Order

        if not order_number and not email:
            return {'error': 'Please provide an order number or email address'}

        orders = Order.objects.all()

        if order_number:
            orders = orders.filter(order_number__iexact=order_number)
        if email:
            orders = orders.filter(email__iexact=email)

        if not orders.exists():
            return {'error': 'No orders found with that information'}

        results = []
        for order in orders[:5]:  # Limit to 5 most recent
            results.append({
                'order_number': order.order_number,
                'status': order.status,
                'status_display': order.get_status_display(),
                'total': float(order.total),
                'created_at': order.created_at.isoformat(),
                'item_count': order.items.count(),
            })

        return {'orders': results}

    except Exception as e:
        return {'error': str(e)}


# ============================================================================
# GIFT CARD TOOLS
# ============================================================================

@tool
def check_gift_card(code: str) -> dict:
    """
    Check the balance of a gift card.

    Use this when a customer wants to check their gift card balance.

    Args:
        code: The gift card code

    Returns:
        Gift card balance and status
    """
    try:
        gift_card = GiftCard.objects.get(code__iexact=code.strip())

        return {
            'code': gift_card.code,
            'balance': float(gift_card.balance),
            'original_amount': float(gift_card.amount),
            'is_active': gift_card.is_active,
            'message': f'Gift card has a balance of ${gift_card.balance:.2f}',
        }

    except GiftCard.DoesNotExist:
        return {'error': 'Gift card not found. Please check the code and try again.'}
    except Exception as e:
        return {'error': str(e)}


# ============================================================================
# MOCKUP TOOLS
# ============================================================================

@tool
def analyze_room_image(image_url: str) -> dict:
    """
    Analyze an uploaded room photo to detect walls for mockup placement.

    Use this when a customer uploads a photo of their room and wants to
    see how a print would look. This initiates the wall detection process.

    Args:
        image_url: URL of the uploaded room image

    Returns:
        Analysis ID and status
    """
    try:
        from apps.mockup.models import WallAnalysis
        from apps.mockup.tasks import analyze_wall_image

        # Create analysis record
        analysis = WallAnalysis.objects.create(
            original_image=image_url,
            status='pending'
        )

        # Trigger async analysis
        analyze_wall_image.delay(str(analysis.id))

        return {
            'analysis_id': str(analysis.id),
            'status': 'processing',
            'message': 'Analyzing your room photo. This may take a moment...',
        }

    except Exception as e:
        return {'error': str(e)}


@tool
def generate_mockup(analysis_id: str, photo_slug: str, variant_id: int) -> dict:
    """
    Generate a mockup showing a print on the analyzed wall.

    Use this after analyze_room_image to show how a specific print
    would look in the customer's space.

    Args:
        analysis_id: The wall analysis ID from analyze_room_image
        photo_slug: The photo to place on the wall
        variant_id: The variant (size) to show

    Returns:
        Mockup image URL or status
    """
    try:
        from apps.mockup.models import WallAnalysis

        analysis = WallAnalysis.objects.get(id=analysis_id)
        photo = Photo.objects.get(slug=photo_slug)
        variant = ProductVariant.objects.get(id=variant_id)

        if analysis.status != 'completed':
            return {
                'status': analysis.status,
                'message': 'Wall analysis is still processing. Please wait a moment.',
            }

        # Return data needed for frontend to render mockup
        return {
            'success': True,
            'analysis': {
                'id': str(analysis.id),
                'wall_image': analysis.original_image.url if analysis.original_image else None,
                'wall_bounds': analysis.wall_bounds,
                'pixels_per_inch': analysis.pixels_per_inch,
            },
            'photo': {
                'slug': photo.slug,
                'title': photo.title,
                'image_url': photo.image.url,
            },
            'variant': {
                'id': variant.id,
                'size': variant.size,
                'width_inches': variant.width_inches,
                'height_inches': variant.height_inches,
            },
            'message': f'Here\'s how "{photo.title}" in {variant.size}" would look in your space!',
        }

    except WallAnalysis.DoesNotExist:
        return {'error': 'Wall analysis not found'}
    except Photo.DoesNotExist:
        return {'error': 'Photo not found'}
    except ProductVariant.DoesNotExist:
        return {'error': 'Variant not found'}
    except Exception as e:
        return {'error': str(e)}


# ============================================================================
# INFO TOOLS
# ============================================================================

@tool
def get_sizing_info() -> str:
    """
    Get sizing guide and recommendations.

    Use this when customers ask about what size to get or how to choose.

    Returns:
        Sizing guide text
    """
    return """## Print Sizing Guide

### Size Recommendations by Space

**Above a Sofa or Couch:**
- Art should be 2/3 to 3/4 the width of the sofa
- 6ft sofa → 30x40" or 40x60" print
- 8ft sectional → 40x60" print

**Above a Bed:**
- Similar to sofa rule - roughly 2/3 the headboard width
- Queen bed → 30x40" or 24x36"
- King bed → 40x60"

**By Wall Size:**
- Small wall (under 5ft wide): 16x24" or 20x30"
- Medium wall (5-8ft wide): 24x36" or 30x40"
- Large wall (8ft+ wide): 40x60" makes a statement

### Available Sizes

**Paper Prints (Matted):**
- 11x14" in 16x20" mat - $175
- 13x19" in 18x24" mat - $250

**Aluminum Prints:**
- 16x24" - $675
- 20x30" - $995
- 24x36" - $1,350
- 30x40" - $1,850
- 30x45" - $2,150
- 40x60" - $3,400

### Tips
- When in doubt, go bigger - undersized art is a common mistake
- Gallery walls can use multiple smaller pieces
- Consider the viewing distance - larger prints for open spaces"""


# ============================================================================
# ALL TOOLS LIST
# ============================================================================

ALL_TOOLS = [
    search_photos_semantic,
    search_photos_filter,
    get_photo_details,
    get_collections,
    add_to_cart,
    get_cart,
    remove_from_cart,
    update_cart_item,
    start_checkout,
    track_order,
    check_gift_card,
    analyze_room_image,
    generate_mockup,
    get_sizing_info,
]
