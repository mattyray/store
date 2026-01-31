"""
Views for the AI chat agent.

Provides SSE streaming endpoint for real-time chat responses.
"""
import json
import time
import uuid

from django.core.cache import cache
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

from .models import Conversation, Message
from .agent import run_agent


def _get_client_ip(request):
    """Get client IP from request, accounting for proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _check_rate_limit(request, scope, max_requests, window_seconds):
    """Simple rate limiter using Django cache. Returns (allowed, retry_after)."""
    ip = _get_client_ip(request)
    cache_key = f'throttle_{scope}_{ip}'
    history = cache.get(cache_key, [])

    now = time.time()
    # Remove expired entries
    history = [t for t in history if now - t < window_seconds]

    if len(history) >= max_requests:
        retry_after = int(window_seconds - (now - history[0]))
        return False, retry_after

    history.append(now)
    cache.set(cache_key, history, window_seconds)
    return True, 0


def get_cart_id_from_request(request):
    """Get or create cart using session key (same as main site's cart system)."""
    from apps.orders.models import Cart

    # Ensure session exists
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return str(cart.id)


def parse_json_body(request):
    """Parse JSON body from request."""
    try:
        body = json.loads(request.body.decode('utf-8'))
        request._body_json = body
        return body
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


@csrf_exempt
@require_http_methods(["POST"])
def chat_stream(request):
    """
    SSE streaming endpoint for chat.

    Accepts POST with JSON body:
    {
        "message": "user message",
        "conversation_id": "optional-uuid",
        "image_url": "optional-image-url",
        "cart_id": "optional-cart-uuid"
    }

    Returns Server-Sent Events stream.
    """
    body = parse_json_body(request)

    user_message = body.get('message', '').strip()
    conversation_id = body.get('conversation_id')
    image_url = body.get('image_url')
    cart_id = body.get('cart_id') or get_cart_id_from_request(request)

    # Allow empty message if image is provided
    if not user_message and not image_url:
        return JsonResponse({'error': 'Message or image is required'}, status=400)

    # Default message for image-only uploads
    if not user_message and image_url:
        user_message = "Here's a photo of my room. Can you help me visualize how a print would look here?"

    # Get or create conversation
    if conversation_id:
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except (Conversation.DoesNotExist, ValueError):
            conversation = Conversation.objects.create()
    else:
        conversation = Conversation.objects.create()

    # Link cart to conversation if provided
    if cart_id and not conversation.cart_id:
        try:
            from apps.orders.models import Cart
            cart = Cart.objects.get(id=cart_id)
            conversation.cart = cart
            conversation.save()
        except Exception:
            pass

    def event_stream():
        """Generator that yields SSE events."""
        try:
            # Send conversation ID first
            yield f"data: {json.dumps({'type': 'conversation_id', 'id': str(conversation.id)})}\n\n"

            # Run agent and stream responses
            for chunk in run_agent(
                conversation=conversation,
                user_message=user_message,
                image_url=image_url,
                cart_id=cart_id,
            ):
                yield f"data: {json.dumps(chunk)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream',
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'  # Disable nginx buffering

    return response


@csrf_exempt
@require_http_methods(["POST"])
def chat_sync(request):
    """
    Non-streaming chat endpoint for testing.

    Same input as chat_stream, but returns complete response as JSON.
    """
    from .agent import run_agent_sync

    body = parse_json_body(request)

    user_message = body.get('message', '').strip()
    if not user_message:
        return JsonResponse({'error': 'Message is required'}, status=400)

    conversation_id = body.get('conversation_id')
    image_url = body.get('image_url')
    cart_id = body.get('cart_id') or get_cart_id_from_request(request)

    # Get or create conversation
    if conversation_id:
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except (Conversation.DoesNotExist, ValueError):
            conversation = Conversation.objects.create()
    else:
        conversation = Conversation.objects.create()

    try:
        response_text = run_agent_sync(
            conversation=conversation,
            user_message=user_message,
            image_url=image_url,
            cart_id=cart_id,
        )

        return JsonResponse({
            'conversation_id': str(conversation.id),
            'response': response_text,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def chat_history(request, conversation_id):
    """
    Get chat history for a conversation.

    Returns all messages in the conversation.
    """
    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except (Conversation.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Conversation not found'}, status=404)

    messages = []
    for msg in conversation.messages.all():
        messages.append({
            'id': msg.id,
            'role': msg.role,
            'content': msg.content,
            'image_url': msg.image_url or None,
            'tool_calls': msg.tool_calls,
            'created_at': msg.created_at.isoformat(),
        })

    return JsonResponse({
        'conversation_id': str(conversation.id),
        'messages': messages,
        'created_at': conversation.created_at.isoformat(),
    })


@csrf_exempt
@require_http_methods(["POST"])
def upload_chat_image(request):
    """
    Upload an image for use in chat (room photos).

    Accepts multipart form with 'image' file.
    Returns the URL of the uploaded image.
    """
    if 'image' not in request.FILES:
        return JsonResponse({'error': 'No image provided'}, status=400)

    image_file = request.FILES['image']

    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    if image_file.content_type not in allowed_types:
        return JsonResponse({'error': 'Invalid image type'}, status=400)

    # Validate file size (max 10MB)
    if image_file.size > 10 * 1024 * 1024:
        return JsonResponse({'error': 'Image too large (max 10MB)'}, status=400)

    try:
        from django.core.files.storage import default_storage
        from django.utils import timezone

        # Generate unique filename
        ext = image_file.name.split('.')[-1] if '.' in image_file.name else 'jpg'
        filename = f"chat-images/{timezone.now().strftime('%Y/%m')}/{uuid.uuid4()}.{ext}"

        # Save to storage (S3 in production)
        path = default_storage.save(filename, image_file)
        url = default_storage.url(path)

        # Make URL absolute for frontend
        if not url.startswith('http'):
            base_url = getattr(settings, 'BACKEND_URL', 'http://localhost:7974')
            url = f"{base_url}{url}"

        return JsonResponse({
            'success': True,
            'url': url,
            'filename': filename,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
