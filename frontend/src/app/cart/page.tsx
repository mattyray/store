'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { getCart, updateCartItem, removeCartItem, createCheckoutSession } from '@/lib/api';
import type { Cart } from '@/types';

export default function CartPage() {
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState<number | null>(null);
  const [checkingOut, setCheckingOut] = useState(false);

  const fetchCart = async () => {
    try {
      const data = await getCart();
      setCart(data);
    } catch (error) {
      console.error('Failed to fetch cart:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  const handleUpdateQuantity = async (itemId: number, quantity: number) => {
    if (quantity < 1) return;
    setUpdating(itemId);
    try {
      await updateCartItem(itemId, quantity);
      await fetchCart();
    } catch (error) {
      console.error('Failed to update quantity:', error);
    } finally {
      setUpdating(null);
    }
  };

  const handleRemove = async (itemId: number) => {
    setUpdating(itemId);
    try {
      await removeCartItem(itemId);
      await fetchCart();
    } catch (error) {
      console.error('Failed to remove item:', error);
    } finally {
      setUpdating(null);
    }
  };

  const handleCheckout = async () => {
    setCheckingOut(true);
    try {
      const { checkout_url } = await createCheckoutSession();
      window.location.href = checkout_url;
    } catch (error) {
      console.error('Failed to create checkout session:', error);
      setCheckingOut(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <h1 className="text-3xl font-light tracking-wide mb-4">Your Cart</h1>
        <p className="text-gray-500 mb-8">Your cart is empty.</p>
        <Link
          href="/photos"
          className="inline-block px-8 py-3 bg-gray-900 text-white text-sm font-medium rounded hover:bg-gray-800 transition"
        >
          Continue Shopping
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-3xl font-light tracking-wide mb-8">Your Cart</h1>

      <div className="space-y-6">
        {cart.items.map((item) => {
          const itemLink = item.item_type === 'variant' && item.variant
            ? `/photos/${item.variant.photo.slug}`
            : item.product
              ? `/book/${item.product.slug}`
              : '#';

          return (
            <div
              key={item.id}
              className="flex gap-6 p-4 bg-gray-50 rounded"
            >
              {/* Image */}
              <div className="relative w-24 h-24 bg-gray-200 rounded overflow-hidden flex-shrink-0">
                {item.image ? (
                  <Image
                    src={item.image}
                    alt={item.title}
                    fill
                    className="object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                    No image
                  </div>
                )}
              </div>

              {/* Details */}
              <div className="flex-1">
                <Link
                  href={itemLink}
                  className="font-medium hover:text-blue-600 transition"
                >
                  {item.title}
                </Link>
                <p className="text-sm text-gray-500 mt-1">{item.description}</p>

                <div className="flex items-center gap-4 mt-3">
                  <div className="flex items-center border border-gray-200 rounded">
                    <button
                      onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                      disabled={updating === item.id || item.quantity <= 1}
                      className="px-3 py-1 text-gray-600 hover:bg-gray-100 disabled:opacity-50"
                    >
                      -
                    </button>
                    <span className="px-3 py-1 min-w-[40px] text-center">{item.quantity}</span>
                    <button
                      onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                      disabled={updating === item.id}
                      className="px-3 py-1 text-gray-600 hover:bg-gray-100 disabled:opacity-50"
                    >
                      +
                    </button>
                  </div>

                  <button
                    onClick={() => handleRemove(item.id)}
                    disabled={updating === item.id}
                    className="text-sm text-red-600 hover:text-red-700 disabled:opacity-50"
                  >
                    Remove
                  </button>
                </div>
              </div>

              {/* Price */}
              <div className="text-right">
                <p className="font-medium">${item.total_price}</p>
                {item.quantity > 1 && (
                  <p className="text-sm text-gray-500">${item.unit_price} each</p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="mt-8 pt-8 border-t border-gray-200">
        <div className="flex justify-between items-center mb-6">
          <span className="text-lg">Subtotal</span>
          <span className="text-2xl font-medium">${cart.subtotal}</span>
        </div>
        <p className="text-sm text-gray-500 mb-6">
          Shipping and taxes calculated at checkout.
        </p>

        <button
          onClick={handleCheckout}
          disabled={checkingOut}
          className="w-full py-4 bg-gray-900 text-white font-medium rounded hover:bg-gray-800 transition disabled:opacity-50"
        >
          {checkingOut ? 'Redirecting to Checkout...' : 'Proceed to Checkout'}
        </button>

        <Link
          href="/photos"
          className="block text-center mt-4 text-sm text-gray-600 hover:text-gray-900"
        >
          Continue Shopping
        </Link>
      </div>
    </div>
  );
}
