"""
LangChain tools for the AI shopping agent.

Each tool is a function the agent can call to take actions
like searching photos, managing cart, generating mockups, etc.
"""
from typing import Optional

from django.conf import settings
from django.db.models import Q

from langchain_core.tools import tool
from openai import OpenAI

from apps.catalog.models import Photo, Collection, ProductVariant
from apps.orders.models import Cart, CartItem
from apps.core.models import GiftCard


def get_openai_client():
    """Get OpenAI client for embeddings."""
    return OpenAI(api_key=settings.OPENAI_API_KEY, timeout=10)


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
        photos = None

        # Try vector search first if OpenAI is configured and photos have embeddings
        try:
            from pgvector.django import CosineDistance

            has_embeddings = Photo.objects.filter(is_active=True, embedding__isnull=False).exists()
            if has_embeddings:
                query_embedding = generate_query_embedding(query)
                # Use pgvector cosine distance - lower is more similar
                photos = Photo.objects.filter(
                    is_active=True,
                    embedding__isnull=False
                ).order_by(
                    CosineDistance('embedding', query_embedding)
                )[:limit]
        except Exception:
            # OpenAI unavailable or quota exceeded - fall back to text search
            pass

        # Fall back to text-based search with stricter matching
        if not photos or not photos.exists():
            # Common stop words to ignore
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
                'dare', 'ought', 'used', 'it', 'its', 'this', 'that', 'these', 'those',
                'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
                'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
                'she', 'her', 'hers', 'herself', 'they', 'them', 'their', 'theirs',
                'what', 'which', 'who', 'whom', 'when', 'where', 'why', 'how',
                'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
                'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
                'very', 'just', 'also', 'now', 'here', 'there', 'then', 'once',
                'photo', 'photos', 'picture', 'pictures', 'image', 'images', 'print',
                'prints', 'art', 'artwork', 'looking', 'want', 'like', 'something',
                'show', 'find', 'get', 'see', 'need', 'any', 'please', 'thanks',
            }

            # Common synonyms to expand search
            synonyms = {
                'relaxing': ['relaxing', 'calming', 'peaceful', 'serene', 'tranquil'],
                'calm': ['calm', 'calming', 'peaceful', 'serene', 'tranquil'],
                'peaceful': ['peaceful', 'calming', 'serene', 'tranquil'],
                'ocean': ['ocean', 'sea', 'water', 'waves', 'coastal'],
                'sea': ['sea', 'ocean', 'water', 'waves', 'coastal'],
                'beach': ['beach', 'sand', 'shore', 'coastal', 'shoreline'],
                'sunset': ['sunset', 'golden', 'dusk', 'evening'],
                'sunrise': ['sunrise', 'dawn', 'morning'],
                'dramatic': ['dramatic', 'striking', 'bold', 'intense'],
                'blue': ['blue', 'azure', 'navy', 'cobalt', 'ocean blue', 'deep blue'],
                'green': ['green', 'emerald', 'seafoam', 'verdant'],
                'aerial': ['aerial', 'overhead', 'bird', 'drone', 'above'],
                'asian': ['asian', 'asia', 'vietnam', 'cambodia', 'thai', 'pagoda', 'temple'],
                'greek': ['greek', 'greece', 'santorini', 'mediterranean'],
                'hamptons': ['hamptons', 'hampton', 'montauk', 'long island'],
            }

            # Extract meaningful search terms
            words = query.lower().split()
            search_terms = [w for w in words if len(w) >= 3 and w not in stop_words]

            if search_terms:
                # Use AND logic - all terms must match somewhere
                # This prevents "asian photos" from matching everything with "photos"
                q_combined = Q()
                for word in search_terms:
                    # Expand word to include synonyms
                    words_to_search = synonyms.get(word, [word])

                    # Build OR query for this term and its synonyms
                    word_match = Q()
                    for search_word in words_to_search:
                        word_match |= (
                            Q(ai_description__icontains=search_word) |
                            Q(title__icontains=search_word) |
                            Q(ai_mood__icontains=search_word) |
                            Q(ai_subjects__icontains=search_word) |
                            Q(description__icontains=search_word) |
                            Q(location__icontains=search_word) |
                            Q(slug__icontains=search_word) |
                            Q(collection__name__icontains=search_word) |
                            Q(ai_colors__icontains=search_word)
                        )
                    q_combined &= word_match  # AND logic between different search terms

                photos = Photo.objects.filter(q_combined).filter(is_active=True).distinct()[:limit]

        # Don't return random photos if nothing matches - let the agent know
        # This is better UX than showing unrelated results
        if not photos or not photos.exists():
            return []

        results = []
        for photo in photos[:limit]:
            price_range = photo.price_range
            results.append({
                'id': photo.id,
                'slug': photo.slug,
                'title': photo.title,
                'description': photo.ai_description or photo.description or f"Beautiful {photo.title} photography print",
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
            'image_url': get_absolute_url(photo.image),
            'thumbnail_url': get_absolute_url(photo.thumbnail) or get_absolute_url(photo.image),
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

        if not cart_id:
            return {'error': 'No cart available. Please refresh the page and try again.'}

        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            return {'error': 'Cart not found. Please refresh the page and try again.'}

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
            'cart_total': float(cart.subtotal),
            'cart_item_count': cart.total_items,
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
                    'subtotal': float(item.total_price),
                })
            elif item.product:
                items.append({
                    'id': item.id,
                    'product_title': item.product.title,
                    'price': float(item.product.price),
                    'quantity': item.quantity,
                    'subtotal': float(item.total_price),
                })

        return {
            'cart_id': str(cart.id),
            'items': items,
            'total': float(cart.subtotal),
            'item_count': cart.total_items,
            'free_shipping': cart.subtotal >= 500,
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
            'cart_total': float(cart.subtotal),
            'cart_item_count': cart.total_items,
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
            'cart_total': float(cart.subtotal),
            'cart_item_count': cart.total_items,
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
    Help the customer proceed to checkout.

    Use this when the customer is ready to purchase. Directs them to the cart
    page where they can click "Proceed to Checkout" to complete payment.

    Args:
        cart_id: Cart ID (will be provided by context)

    Returns:
        Cart URL and instructions
    """
    try:
        if not cart_id:
            return {'error': 'No cart found'}

        cart = Cart.objects.get(id=cart_id)

        if cart.total_items == 0:
            return {'error': 'Cart is empty'}

        # Get cart items for summary
        items = []
        for item in cart.items.all():
            if item.variant:
                items.append(f"{item.variant.photo.title} ({item.variant.display_name})")
            elif item.product:
                items.append(item.product.title)

        return {
            'success': True,
            'cart_url': f"{settings.FRONTEND_URL}/cart",
            'cart_total': float(cart.subtotal),
            'item_count': cart.total_items,
            'items': items,
            'free_shipping': cart.subtotal >= 500,
            'message': 'Your cart is ready! Click the cart link or use the "Proceed to Checkout" button on the cart page to complete your purchase with Stripe.',
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

        if not order_number or not email:
            return {'error': 'Please provide both an order number and email address to look up an order'}

        orders = Order.objects.filter(
            order_number__iexact=order_number,
            customer_email__iexact=email,
        )

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

        if not gift_card.is_valid:
            # Return same generic message as web endpoint to prevent
            # enumeration of valid vs invalid/expired codes
            return {'valid': False, 'error': 'This gift card is not valid'}

        return {
            'valid': True,
            'balance': float(gift_card.remaining_balance),
            'message': f'Gift card has a balance of ${gift_card.remaining_balance:.2f}',
        }

    except GiftCard.DoesNotExist:
        # Same message as valid-but-expired to prevent code enumeration
        return {'valid': False, 'error': 'This gift card is not valid'}
    except Exception:
        return {'valid': False, 'error': 'This gift card is not valid'}


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
        Analysis ID and status, or helpful message if analysis unavailable
    """
    # Check if URL is HTTPS (required for Claude Vision API)
    if image_url.startswith('http://'):
        return {
            'status': 'unavailable',
            'message': 'Room visualization is available in production. For now, I can help you choose the right size based on your wall dimensions! What are the approximate dimensions of the wall where you want to hang the print?',
            'suggestion': 'Tell me your wall width and I can recommend the perfect print size.',
        }

    # SSRF protection: only fetch images from our own S3 bucket
    allowed_domain = settings.AWS_S3_CUSTOM_DOMAIN
    if allowed_domain and not image_url.startswith(f'https://{allowed_domain}/'):
        return {'error': 'Invalid image URL. Please upload your room photo using the upload button.'}

    try:
        import requests
        from django.core.files.base import ContentFile
        from apps.mockup.models import WallAnalysis
        from apps.mockup.tasks import analyze_wall_image

        # Download image from our S3 bucket
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()

        # Determine file extension from content type
        content_type = response.headers.get('content-type', 'image/jpeg')
        ext = 'jpg'
        if 'png' in content_type:
            ext = 'png'
        elif 'webp' in content_type:
            ext = 'webp'

        # Create analysis record with downloaded image
        analysis = WallAnalysis.objects.create(status='pending')
        analysis.original_image.save(
            f'room_{analysis.id}.{ext}',
            ContentFile(response.content),
            save=True
        )

        # Trigger async analysis
        analyze_wall_image.delay(str(analysis.id))

        return {
            'analysis_id': str(analysis.id),
            'status': 'processing',
            'message': 'Analyzing your room photo. This may take a moment...',
        }

    except ImportError:
        # Mockup app not installed
        return {
            'status': 'unavailable',
            'message': 'I can see your room photo! While the automatic mockup feature is being set up, I can help you choose the right size. What are the approximate dimensions of that wall?',
        }
    except Exception as e:
        return {'error': str(e)}


@tool
def generate_mockup(
    analysis_id: str,
    photo_slug: str,
    size: str,
    material: str = "aluminum",
    variant_id: Optional[int] = None
) -> dict:
    """
    Generate a mockup showing a print on the analyzed wall.

    Use this after analyze_room_image to show how a specific print
    would look in the customer's space. This tool will wait for the
    wall analysis to complete if it's still processing.

    IMPORTANT: Use the `size` and `material` parameters to specify the variant.
    The size should match exactly what the customer requested (e.g., "20x30", "24x36", "40x60").
    The material should be "aluminum" or "paper" based on what the customer wants.

    Args:
        analysis_id: The wall analysis ID from analyze_room_image
        photo_slug: The photo to place on the wall
        size: The print size (e.g., "20x30", "24x36", "40x60" for aluminum, "11x14", "13x19" for paper)
        material: The material type - "aluminum" (default) or "paper"
        variant_id: (DEPRECATED) Optional variant ID - prefer using size and material instead

    Returns:
        Mockup data with wall image and placement info, or error
    """
    try:
        from apps.mockup.models import WallAnalysis

        analysis = WallAnalysis.objects.get(id=analysis_id)
        photo = Photo.objects.get(slug=photo_slug)

        # Find variant by size and material (preferred), or by variant_id (fallback)
        variant = None
        if size and material:
            # Normalize size format - handle both "20x30" and "30x20" formats
            size_normalized = size.strip().lower()
            # Try exact match first
            variant = ProductVariant.objects.filter(
                photo=photo,
                material__iexact=material.strip(),
                is_available=True
            ).filter(
                Q(size__icontains=size_normalized) |
                Q(size__icontains='x'.join(size_normalized.split('x')[::-1]))  # Try reversed dimensions
            ).first()

            # If no match, try matching just the dimensions in either order
            if not variant:
                size_parts = size_normalized.replace('"', '').replace("'", '').split('x')
                if len(size_parts) == 2:
                    try:
                        w, h = int(size_parts[0].strip()), int(size_parts[1].strip())
                        # Find variant where dimensions match in either order
                        for v in ProductVariant.objects.filter(photo=photo, material__iexact=material.strip(), is_available=True):
                            if (v.width_inches == w and v.height_inches == h) or (v.width_inches == h and v.height_inches == w):
                                variant = v
                                break
                    except ValueError:
                        pass

        # Fallback to variant_id if provided and size/material didn't find anything
        if not variant and variant_id:
            variant = ProductVariant.objects.get(id=variant_id)

        if not variant:
            # List available variants to help the agent
            available = ProductVariant.objects.filter(photo=photo, is_available=True)
            available_list = [f"{v.size} ({v.material})" for v in available]
            return {
                'error': f'Could not find a {material} variant in size {size} for "{photo.title}". Available options: {", ".join(available_list)}',
            }

        # Refresh to check current status without blocking
        analysis.refresh_from_db()

        if analysis.status == 'failed':
            return {
                'error': 'Wall detection failed. Please try uploading a different room photo.',
                'status': 'failed',
            }

        if analysis.status in ('pending', 'processing'):
            return {
                'status': 'processing',
                'analysis_id': str(analysis.id),
                'message': 'Wall analysis is still processing. The mockup tool on the page will show the result when ready. Please let the customer know to check the "See In Your Room" tool.',
            }

        # Return mockup data for frontend rendering
        return {
            'success': True,
            'type': 'mockup',  # Helps frontend identify this as mockup data
            'analysis': {
                'id': str(analysis.id),
                'wall_image_url': get_absolute_url(analysis.original_image),
                'wall_bounds': analysis.wall_bounds,
                'pixels_per_inch': analysis.pixels_per_inch,
                'confidence': analysis.confidence,
            },
            'photo': {
                'slug': photo.slug,
                'title': photo.title,
                'image_url': get_absolute_url(photo.image),
                'thumbnail_url': get_absolute_url(photo.thumbnail) or get_absolute_url(photo.image),
            },
            'variant': {
                'id': variant.id,
                'size': variant.size,
                'material': variant.material,
                'width_inches': variant.width_inches,
                'height_inches': variant.height_inches,
                'price': float(variant.price),
            },
            'message': f'Here\'s how "{photo.title}" ({variant.size}) would look in your space!',
        }

    except WallAnalysis.DoesNotExist:
        return {'error': 'Wall analysis not found. Please upload a room photo first.'}
    except Photo.DoesNotExist:
        return {'error': f'Photo not found: {photo_slug}'}
    except ProductVariant.DoesNotExist:
        return {'error': f'Size/variant not found: {variant_id}'}
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
