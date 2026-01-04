export interface Collection {
  id: number;
  name: string;
  slug: string;
  description: string;
  cover_image: string | null;
  is_limited_edition: boolean;
  photo_count: number;
}

export interface Photo {
  id: number;
  title: string;
  slug: string;
  collection: {
    id: number;
    name: string;
    slug: string;
  };
  image: string;
  thumbnail: string | null;
  description: string;
  location: string;
  location_tag: string;
  orientation: 'horizontal' | 'vertical' | 'square';
  is_featured: boolean;
  min_price: string | null;
  variants?: ProductVariant[];
}

export interface ProductVariant {
  id: number;
  size: string;
  material: 'paper' | 'aluminum';
  price: string;
  width_inches: number;
  height_inches: number;
  is_available: boolean;
  display_name: string;
}

export interface CartItem {
  id: number;
  variant: ProductVariant & {
    photo: {
      id: number;
      title: string;
      slug: string;
      thumbnail: string | null;
    };
  };
  quantity: number;
  total_price: string;
}

export interface Cart {
  items: CartItem[];
  subtotal: string;
  item_count: number;
}

export interface Order {
  order_number: string;
  customer_email: string;
  total: string;
  status: string;
}

export interface GiftCardCheck {
  valid: boolean;
  balance?: string;
  expires_at?: string;
  error?: string;
}

export interface ApiResponse<T> {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
}
