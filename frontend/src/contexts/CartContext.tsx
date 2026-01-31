'use client';

import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getCart } from '@/lib/api';
import type { Cart } from '@/types';

interface CartContextValue {
  cart: Cart | null;
  loading: boolean;
  itemCount: number;
  refreshCart: () => Promise<void>;
}

const CartContext = createContext<CartContextValue>({
  cart: null,
  loading: true,
  itemCount: 0,
  refreshCart: async () => {},
});

export function useCart() {
  return useContext(CartContext);
}

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshCart = useCallback(async () => {
    try {
      const data = await getCart();
      setCart(data);
    } catch {
      // Silently fail - cart will show as empty
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshCart();
  }, [refreshCart]);

  const itemCount = cart?.total_items ?? 0;

  return (
    <CartContext.Provider value={{ cart, loading, itemCount, refreshCart }}>
      {children}
    </CartContext.Provider>
  );
}
