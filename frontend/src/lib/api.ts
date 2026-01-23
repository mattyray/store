// Server-side uses internal Docker network, client-side uses browser-accessible URL
const getApiUrl = () => {
  if (typeof window === 'undefined') {
    // Server-side: use Docker service name
    return process.env.INTERNAL_API_URL || 'http://backend:7974/api';
  }
  // Client-side: use browser-accessible URL
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7974/api';
};

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${getApiUrl()}${endpoint}`;
  const isServer = typeof window === 'undefined';

  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    // Only include credentials on client-side requests
    ...(isServer ? { cache: 'no-store' } : { credentials: 'include' }),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(error.error || `HTTP ${res.status}`);
  }

  return res.json();
}

// Collections
export async function getCollections() {
  return fetchApi<{ results: import('@/types').Collection[] }>('/collections/');
}

export async function getCollection(slug: string) {
  return fetchApi<import('@/types').Collection & { photos: import('@/types').Photo[] }>(
    `/collections/${slug}/`
  );
}

// Photos
export async function getPhotos(params?: Record<string, string>) {
  const query = params ? `?${new URLSearchParams(params)}` : '';
  return fetchApi<{ results: import('@/types').Photo[] }>(`/photos/${query}`);
}

export async function getFeaturedPhotos() {
  return fetchApi<import('@/types').Photo[]>('/photos/featured/');
}

export async function getPhoto(slug: string) {
  return fetchApi<import('@/types').Photo>(`/photos/${slug}/`);
}

// Products
export async function getProducts(params?: Record<string, string>) {
  const query = params ? `?${new URLSearchParams(params)}` : '';
  return fetchApi<{ results: import('@/types').Product[] }>(`/products/${query}`);
}

export async function getProduct(slug: string) {
  return fetchApi<import('@/types').Product>(`/products/${slug}/`);
}

// Cart
export async function getCart() {
  return fetchApi<import('@/types').Cart>('/cart/');
}

export async function addToCart(variantId: number, quantity: number = 1) {
  return fetchApi<import('@/types').CartItem>('/cart/items/', {
    method: 'POST',
    body: JSON.stringify({ variant_id: variantId, quantity }),
  });
}

export async function addProductToCart(productId: number, quantity: number = 1) {
  return fetchApi<import('@/types').CartItem>('/cart/items/', {
    method: 'POST',
    body: JSON.stringify({ product_id: productId, quantity }),
  });
}

export async function updateCartItem(itemId: number, quantity: number) {
  return fetchApi<import('@/types').CartItem>(`/cart/items/${itemId}/`, {
    method: 'PUT',
    body: JSON.stringify({ quantity }),
  });
}

export async function removeCartItem(itemId: number) {
  return fetchApi<void>(`/cart/items/${itemId}/`, {
    method: 'DELETE',
  });
}

export async function clearCart() {
  return fetchApi<void>('/cart/', {
    method: 'DELETE',
  });
}

// Checkout
export async function createCheckoutSession(giftCardCode?: string) {
  return fetchApi<{ checkout_url: string; session_id: string }>('/checkout/', {
    method: 'POST',
    body: JSON.stringify({ gift_card_code: giftCardCode }),
  });
}

export async function getOrderBySession(sessionId: string) {
  return fetchApi<import('@/types').Order>(`/order/?session_id=${sessionId}`);
}

// Newsletter
export async function subscribeNewsletter(email: string, name?: string) {
  return fetchApi<{ success: boolean; message: string }>('/newsletter/subscribe/', {
    method: 'POST',
    body: JSON.stringify({ email, name }),
  });
}

// Gift Cards
export async function purchaseGiftCard(data: {
  amount: number;
  recipient_email: string;
  recipient_name?: string;
  purchaser_email: string;
  purchaser_name?: string;
  message?: string;
}) {
  return fetchApi<{ checkout_url: string; session_id: string }>('/gift-cards/purchase/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function checkGiftCard(code: string) {
  return fetchApi<import('@/types').GiftCardCheck>('/gift-cards/check/', {
    method: 'POST',
    body: JSON.stringify({ code }),
  });
}

// Contact
export async function submitContactForm(data: {
  name: string;
  email: string;
  subject?: string;
  message: string;
}) {
  return fetchApi<{ success: boolean }>('/contact/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// Order Tracking
export async function trackOrder(email: string, orderNumber: string) {
  return fetchApi<{
    order_number: string;
    status: string;
    tracking_number?: string;
    tracking_carrier?: string;
    tracking_url?: string;
  }>('/orders/track/', {
    method: 'POST',
    body: JSON.stringify({ email, order_number: orderNumber }),
  });
}

// Wall Mockup
export async function uploadWallImage(file: File): Promise<import('@/types').WallAnalysis> {
  const formData = new FormData();
  formData.append('image', file);

  const url = `${getApiUrl()}/mockup/analyze/`;
  const res = await fetch(url, {
    method: 'POST',
    body: formData,
    credentials: 'include',
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ error: 'Upload failed' }));
    throw new Error(error.error || `HTTP ${res.status}`);
  }

  return res.json();
}

export async function getWallAnalysis(analysisId: string) {
  return fetchApi<import('@/types').WallAnalysis>(`/mockup/analyze/${analysisId}/`);
}

export async function updateWallAnalysis(
  analysisId: string,
  data: {
    wall_bounds?: { top: number; bottom: number; left: number; right: number };
    wall_height_feet?: number;
  }
) {
  return fetchApi<import('@/types').WallAnalysis>(`/mockup/analyze/${analysisId}/`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function saveMockup(data: {
  analysis_id: string;
  mockup_image: string;
  config: import('@/types').MockupConfig;
}) {
  return fetchApi<import('@/types').SavedMockup>('/mockup/save/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getMockup(mockupId: string) {
  return fetchApi<import('@/types').SavedMockup>(`/mockup/${mockupId}/`);
}

export async function pollWallAnalysis(
  analysisId: string,
  onProgress?: (status: string) => void,
  maxAttempts = 30,
  intervalMs = 1000
): Promise<import('@/types').WallAnalysis> {
  for (let i = 0; i < maxAttempts; i++) {
    const analysis = await getWallAnalysis(analysisId);
    if (onProgress) onProgress(analysis.status);

    if (['completed', 'failed', 'manual'].includes(analysis.status)) {
      return analysis;
    }

    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }

  throw new Error('Analysis timed out');
}

// Chat API
export interface ChatMessage {
  role: 'user' | 'assistant' | 'tool';
  content: string;
  image_url?: string;
  tool_calls?: Array<{ id: string; name: string; args: Record<string, unknown> }>;
}

export interface ChatChunk {
  type: 'conversation_id' | 'text' | 'tool_use' | 'tool_result' | 'error' | 'done';
  id?: string;
  content?: string;
  tool?: string;
  args?: Record<string, unknown>;
  result?: unknown;
  message?: string;
}

export async function* streamChat(
  message: string,
  conversationId?: string,
  imageUrl?: string,
  cartId?: string
): AsyncGenerator<ChatChunk> {
  const url = `${getApiUrl()}/chat/`;

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      image_url: imageUrl,
      cart_id: cartId,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Chat request failed' }));
    yield { type: 'error', message: error.error || `HTTP ${response.status}` };
    return;
  }

  const reader = response.body?.getReader();
  if (!reader) {
    yield { type: 'error', message: 'No response body' };
    return;
  }

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      // Process any remaining data in buffer
      if (buffer.trim()) {
        const lines = buffer.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              yield data as ChatChunk;
            } catch {
              // Skip malformed JSON
            }
          }
        }
      }
      break;
    }

    buffer += decoder.decode(value, { stream: true });

    // Process complete SSE messages
    const lines = buffer.split('\n');
    buffer = lines.pop() || ''; // Keep incomplete line in buffer

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6));
          console.log('[API] SSE chunk:', data.type);
          yield data as ChatChunk;
        } catch (e) {
          console.error('[API] Parse error:', line.slice(0, 100), e);
        }
      }
    }
  }
}

export async function getChatHistory(conversationId: string) {
  return fetchApi<{
    conversation_id: string;
    messages: ChatMessage[];
    created_at: string;
  }>(`/chat/history/${conversationId}/`);
}

export async function uploadChatImage(file: File): Promise<{ url: string }> {
  const formData = new FormData();
  formData.append('image', file);

  const url = `${getApiUrl()}/chat/upload-image/`;
  const res = await fetch(url, {
    method: 'POST',
    body: formData,
    credentials: 'include',
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ error: 'Upload failed' }));
    throw new Error(error.error || `HTTP ${res.status}`);
  }

  return res.json();
}
