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
  collection_name: string;
  collection_slug: string;
  image: string;
  thumbnail: string | null;
  description: string;
  location: string;
  location_tag: string;
  orientation: string;
  orientation_display: string;
  is_featured: boolean;
  price_range: { min: number; max: number } | null;
  variants?: ProductVariant[];
  created_at: string;
  aspect_ratio?: number;
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
  item_type: 'variant' | 'product';
  variant?: ProductVariant & {
    photo: {
      id: number;
      title: string;
      slug: string;
      thumbnail: string | null;
    };
  };
  product?: {
    id: number;
    title: string;
    slug: string;
    image: string;
    product_type: string;
  };
  quantity: number;
  unit_price: string;
  total_price: string;
  title: string;
  description: string;
  image: string | null;
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

export interface Product {
  id: number;
  title: string;
  slug: string;
  product_type: 'book' | 'merch';
  product_type_display: string;
  description: string;
  long_description?: string;
  image: string;
  additional_images?: string[];
  price: string;
  compare_at_price?: string;
  is_in_stock: boolean;
  is_on_sale: boolean;
  is_featured: boolean;
  author?: string;
  publisher?: string;
  publication_year?: number;
  pages?: number;
  dimensions?: string;
  isbn?: string;
  stock_quantity?: number;
}

export interface ApiResponse<T> {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
}

// Wall Mockup Types
export interface WallAnalysis {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'manual';
  original_image: string;
  original_width: number | null;
  original_height: number | null;
  depth_map: string | null;
  wall_mask: string | null;
  wall_bounds: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  } | null;
  confidence: number | null;
  pixels_per_inch: number | null;
  wall_height_feet: number;
  error_message: string;
  created_at: string;
  completed_at: string | null;
}

export interface SavedMockup {
  id: string;
  wall_analysis: string;
  mockup_image: string;
  config: MockupConfig;
  share_url: string;
  created_at: string;
}

export interface MockupConfig {
  prints: Array<{
    photo_id: number;
    variant_id: number;
    position: { x: number; y: number };
    scale?: number;
  }>;
  wall_height_feet: number;
}

export interface MockupPrint {
  id: string;
  photo: Photo;
  variant: ProductVariant;
  position: { x: number; y: number };
}
